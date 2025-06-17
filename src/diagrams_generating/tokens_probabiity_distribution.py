import matplotlib.pyplot as plt


# no safe choice
results = ["R5C4", "R5C3", "R5C2", "R5C0", "R3C4", "R5C1", "R4C3", "R3C5", "R3C1", "R5C5"]
probabilities = [0.07048030942678452, 0.041993360966444016, 0.03614870458841324, 0.03269480913877487, 0.03229221701622009, 0.02980448491871357, 0.026404479518532753, 0.022604750469326973, 0.022539934143424034, 0.021986857056617737]

# # safe choice
# results = ["R3C1", "R3C3", "R4C2", "R2C2", "<START>", "<END>", "<DEAD>", "<HELPER_TAG>", "S0", "S1"]
# probabilities = [0.36472830176353455, 0.2884289026260376, 0.21908995509147644, 0.12775278091430664, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

# Create a horizontal bar plot
plt.figure(figsize=(10, 6))
plt.barh(results, probabilities, color='skyblue')
plt.gca().invert_yaxis()  # Invert y-axis to have the highest probability at the top

# Add titles and labels
plt.ylabel('Token Name')
plt.xlabel('Probability')
plt.title('Probability with Token Name')
plt.tight_layout()

# Show the plot
plt.show()