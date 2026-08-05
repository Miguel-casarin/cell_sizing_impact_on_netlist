import sys
import traceback

def fatal(context_msg: str, error: Exception, debug_file, error_file):
    
    full_msg = f"{context_msg}: {error}\n{traceback.format_exc()}"
    print(f"ERRO FATAL NO SETUP: {full_msg}")
    debug_file.write(f"ERRO FATAL NO SETUP: {full_msg}\n")
    error_file.write(f"ERRO FATAL NO SETUP: {full_msg}\n")
    debug_file.flush()
    error_file.flush()
    debug_file.close()
    error_file.close()
    sys.exit(1)