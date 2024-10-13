from utils.code_time import get_code_time

def main():
    try:
        print("Starting get_code_time() function")  # Add this
        Focus, ACT, CT = get_code_time()
        print(f"Results - Focus: {Focus}, ACT: {ACT}, CT: {CT}")
    except Exception as e:
        print("Error:", e)

# if __name__ == "__main__":
main()
