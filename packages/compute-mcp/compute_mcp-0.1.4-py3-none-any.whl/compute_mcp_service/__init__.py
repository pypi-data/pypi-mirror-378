import argparse
from .server import mcp
def main():
    parser = argparse.ArgumentParser(
        description="compute_mcp_service desc",
    )
    parser.parse_args()
    mcp.run()
if __name__ == "__main__":
    main()