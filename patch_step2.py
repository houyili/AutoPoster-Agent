import os
import re

with open("step2_generator.py", "r") as f:
    content = f.read()

old_block = """            else:
                print("⚠️  Compilation failed. Errors:")
                print(result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr)"""

new_block = """            else:
                print("⚠️  Compilation failed. Errors:")
                err_msg = result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr
                print(err_msg)
                with open("compilation_error.log", "w") as f:
                    f.write(err_msg)
        finally:
            if 'result' in locals() and result.returncode == 0 and os.path.exists("compilation_error.log"):
                os.remove("compilation_error.log")"""

if old_block in content:
    content = content.replace(old_block, new_block)
    with open("step2_generator.py", "w") as f:
        f.write(content)
    print("Patched step2_generator.py successfully.")
else:
    print("Could not find block to patch.")
