from tqdm import tqdm
from src.llm_vs_agent.llm_gameplay import main
import os

# standard position model vs random agent
output_dir = "/Users/szymon/Documents/Bachelor-Thesis/src/llm_vs_agent/tournaments"
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, "standard_pos_256_context_vs_bfs.txt")



with open(output_file, "w") as f:
    f.write("Standard Position Model vs BFS Agent Competition\n")
    f.write("================================================\n\n")

scores = {"standard_pos": 0, "agent": 0}

for i in tqdm(range(100)):
    igen, winner, state = main(model="out-standard_pos")
    if winner == "llm":
        scores["standard_pos"] += 1
    else:
        scores["agent"] += 1
        
    with open(output_file, "a") as f:
        f.write(f"Game {i+1}:\n")
        f.write(f"Improper generations: {igen}\n")
        f.write(f"Snake0 head: {state.snakes[0].head}\n")
        f.write(f"Snake0 tail: {state.snakes[0].tail}\n")
        f.write(f"Snake1 head: {state.snakes[1].head}\n")
        f.write(f"Snake1 tail: {state.snakes[1].tail}\n")
        f.write(f"Turns {state.turn}\n")
        f.write(f"Winner: {winner}\n")
        f.write("=========================\n\n")
    
    if (i+1) % 10 == 0:
        print(f"Completed {i+1}/100 games. Current score: {scores}")

with open(output_file, "a") as f:
    f.write("\nFinal Results:\n")
    f.write(f"Standard Position Model: {scores['standard_pos']} wins\n")
    f.write(f"Random Agent: {scores['agent']} wins\n")

print(f"\nResults saved to {output_file}")
print(f"Final scores: {scores}")