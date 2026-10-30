import json, sys, re
nb = json.load(open(sys.argv[1]))
errs, ticks, crosses, blanks = [], 0, 0, 0
for i, c in enumerate(nb["cells"]):
    if c["cell_type"] != "code": continue
    for o in c.get("outputs", []):
        if o.get("output_type") == "error":
            errs.append((i, o["ename"], o["evalue"][:150]))
        txt = "".join(o.get("text", "")) if o.get("output_type") == "stream" else ""
        ticks += txt.count("✅ "); crosses += txt.count("❌"); blanks += txt.count("✍️")
        for line in txt.splitlines():
            if line.startswith(("✅","❌","You have","🏆","💪")): print(f"   [{i}] {line[:140]}")
print("ERRORS:", errs); print("ticks", ticks, "crosses", crosses, "blank-msgs", blanks)
