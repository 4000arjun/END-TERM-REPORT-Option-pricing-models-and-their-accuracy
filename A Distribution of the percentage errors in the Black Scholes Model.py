import matplotlib.pyplot as plt
import seaborn as sns

if 'Pricing_Error' not in options_df.columns or 'Percentage_Error' not in options_df.columns:
    options_df['Pricing_Error'] = options_df['Black_Scholes_Price'] - options_df['Option_Close']
    options_df['Percentage_Error'] = options_df.apply(
        lambda row: (row['Pricing_Error'] / row['Option_Close']) * 100 if row['Option_Close'] != 0 else float('inf'),
        axis=1
    )
    options_df['Absolute_Percentage_Error'] = options_df['Percentage_Error'].abs()

errors_to_plot = options_df[options_df['Percentage_Error'] != float('inf')]['Percentage_Error']

if not errors_to_plot.empty:
    plt.figure(figsize=(10, 6))
    sns.histplot(errors_to_plot, bins=50, kde=True)
    plt.title('Distribution of Black-Scholes Pricing Percentage Errors')
    plt.xlabel('Percentage Error (%)')
    plt.ylabel('Frequency')
    plt.grid(True)
    plt.show()
else:
    print("No valid percentage errors to plot (all options had a market price of zero).")
