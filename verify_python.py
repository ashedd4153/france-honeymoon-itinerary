
import sys
try:
    with open("proof.txt", "w") as f:
        f.write("I am alive")
except Exception as e:
    sys.exit(2)
sys.exit(1)
