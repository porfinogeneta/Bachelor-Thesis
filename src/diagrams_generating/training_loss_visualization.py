import matplotlib.pyplot as plt
import re
import io

# In a real application, you would read this from a file, 
# e.g., with open('log.txt', 'r') as f:
# log_data = f.read()

with open("/Users/szymon/Documents/Bachelor-Thesis/src/diagrams_generating/loss_4k.txt", 'r') as f:
    log_data = f.read()

# --- Data Storage ---
# We'll store the parsed data in dictionaries
iter_data = {'iterations': [], 'losses': []}
step_data = {'steps': [], 'train_losses': [], 'val_losses': []}

# --- Parsing Logic ---
# Regex patterns to find the data in each line
iter_pattern = re.compile(r"iter (\d+): loss ([\d\.]+)")
step_pattern = re.compile(r"step (\d+): train loss ([\d\.]+)?, val loss ([\d\.]+)?")

# Use io.StringIO to simulate reading from a file line by line
log_file = io.StringIO(log_data)

for line in log_file:
    # Clean up the line
    line = line.strip()
    if not line or line.startswith('....'):
        continue

    # Try to match the 'iter' pattern
    iter_match = iter_pattern.match(line)
    if iter_match:
        iter_data['iterations'].append(int(iter_match.group(1)))
        iter_data['losses'].append(float(iter_match.group(2)))
        continue

    # If it's not an 'iter' line, try to match the 'step' pattern
    step_match = step_pattern.match(line)
    if step_match:
        step_data['steps'].append(int(step_match.group(1)))
        step_data['train_losses'].append(float(step_match.group(2)))
        step_data['val_losses'].append(float(step_match.group(3)))
        continue

# --- Plotting Logic ---
# Set a nice style for the plot
plt.style.use('seaborn-v0_8-whitegrid')
plt.figure(figsize=(15, 8))

# Plot iteration loss as a continuous line
plt.plot(
    iter_data['iterations'], 
    iter_data['losses'], 
    label='Iteration Loss', 
    color='darkgray', 
    alpha=0.8, 
    linewidth=1.5
)

# Plot train loss from 'step' lines as distinct blue dots
plt.scatter(
    step_data['steps'], 
    step_data['train_losses'], 
    label='Train Loss (at step)', 
    color='#007acc',  # A nice blue
    s=55, 
    zorder=5, # Ensures dots are drawn on top of the line
    edgecolors='white'
)

# Plot validation loss from 'step' lines as distinct red dots
plt.scatter(
    step_data['steps'], 
    step_data['val_losses'], 
    label='Validation Loss (at step)', 
    color='#e53e3e', # A nice red
    s=25, 
    zorder=5,
    edgecolors='white'
)

# --- Final Touches for a Professional Look ---
plt.title('Training and Validation Loss Over Iterations', fontsize=18, fontweight='bold')
plt.xlabel('Iterations', fontsize=14)
plt.ylabel('Loss Value', fontsize=14)
plt.legend(fontsize=12, frameon=True, shadow=True)
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.tight_layout() # Adjusts plot to ensure everything fits without overlapping

# Display the plot
plt.show()

