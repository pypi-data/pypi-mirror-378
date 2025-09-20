import subprocess
import os
import tempfile

def run_cpp(file=None, text=None):
    if not file and not text:
        raise ValueError("Either 'file' or 'text' must be provided.")

    mingw_bin = r"D:\ijraa\winlibs-extracted\mingw32\bin"
    gpp_path = os.path.join(mingw_bin, "g++.exe")
    
    if file:
        cpp_file = os.path.abspath(f"D:\\ijraa\\{file}.cpp")
        exe_file = os.path.abspath(f"D:\\ijraa\\winlibs-extracted\\mingw32\\bin\\code_files\\{file}.exe")
    else:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".cpp", dir="D:\\ijraa")
        cpp_file = tmp.name
        exe_file = cpp_file.replace(".cpp", ".exe")
        tmp.write(text.encode())
        tmp.close()

    # compile
    compile_cmd = [gpp_path, cpp_file, "-o", exe_file]
    try:
        subprocess.run(compile_cmd, check=True, capture_output=True, text=True)
        print(f"Compiled {cpp_file} -> {exe_file}")
    except subprocess.CalledProcessError as e:
        print("Compilation failed!")
        print("Compiler output:\n", e.stdout)
        print("Compiler errors:\n", e.stderr)
        return

    # run the executable with MinGW bin in PATH
    try:
        env = os.environ.copy()
        env["PATH"] = mingw_bin + ";" + env.get("PATH", "")
        result = subprocess.run(exe_file, capture_output=True, text=True, shell=True, env=env)
        print("Output:\n", result.stdout.strip())
        if result.stderr:
            print("Errors:\n", result.stderr)
    except Exception as e:
        print("Execution failed:", e)
    finally:
        if text:
            os.remove(cpp_file)
            os.remove(exe_file)

# Example usage:
run_cpp(file="test")
# run_cpp(text='#include <iostream>\nint main(){std::cout<<"Hello World\\n"; return 0;}')
