import os
import sys

def main():
    os.environ["STREAMLIT_SERVER_PORT"] = "7860"
    os.environ["STREAMLIT_SERVER_ADDRESS"] = "0.0.0.0"
    os.system(f"{sys.executable} -m streamlit run ui/app.py")

if __name__ == "__main__":
    main()
