"""极简 frontmatter 工具：只处理本仓规范的顶层标量/行内列表，其余原样保留。"""
import re
def split(text):
    if not text.startswith("---\n"): return {}, text
    end = text.find("\n---\n", 4)
    if end < 0: return {}, text
    return text[4:end], text[end+5:]
def parse(text):
    head, body = split(text)
    data = {}
    if isinstance(head, dict): return data, body
    for line in head.splitlines():
        m = re.match(r"^([a-z_]+):\s*(.*)$", line)
        if not m: continue
        k, v = m.group(1), m.group(2).strip()
        if v.startswith("[") and v.endswith("]"):
            inner = v[1:-1].strip()
            data[k] = [x.strip().strip('"\'') for x in inner.split(",")] if inner else []
        else:
            data[k] = v.strip('"\'')
    return data, body
def set_fields(text, updates, history_entry=None):
    head, body = split(text)
    lines = head.splitlines()
    seen = set()
    out = []
    for line in lines:
        m = re.match(r"^([a-z_]+):", line)
        if m and m.group(1) in updates:
            k = m.group(1); seen.add(k)
            v = updates[k]
            if isinstance(v, list): v = "[" + ", ".join(v) + "]"
            out.append(f"{k}: {v}")
        else:
            out.append(line)
    for k, v in updates.items():
        if k not in seen:
            if isinstance(v, list): v = "[" + ", ".join(v) + "]"
            out.append(f"{k}: {v}")
    if history_entry:
        # 在 history: 行后追加一条
        final=[]; inserted=False
        for i,line in enumerate(out):
            final.append(line)
            if line.strip()=="history:" and not inserted:
                final.append(f"  - {history_entry}"); inserted=True
        out=final
    return "---\n" + "\n".join(out) + "\n---\n" + body
