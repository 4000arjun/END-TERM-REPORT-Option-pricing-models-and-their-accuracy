if 'options_df' in locals() and not options_df.empty:
    processed_rows = len(options_df)
    average_absolute_error = options_df[options_df['Absolute_Percentage_Error'] != float('inf')]['Absolute_Percentage_Error'].mean()

    print("\n" + "="*55)
    print("                      QUANTITATIVE SUMMARY")
    print("="*55)
    print(f"  Total Options Processed:    {processed_rows}")

    
    option_counts = options_df['Option_Type'].value_counts()
    for option_type, count in option_counts.items():
        print(f"  Number of {option_type.capitalize()} Options: {count}")

    if not pd.isna(average_absolute_error):
        print(f"  Average Absolute Error:     {average_absolute_error:.2f}%")
    else:
        print("  Average Absolute Error:     Could not be calculated (all options had zero market price).")
    call_options_df = options_df[(options_df['Option_Type'].str.lower() == 'call') & (options_df['Absolute_Percentage_Error'] != float('inf'))]
    put_options_df = options_df[(options_df['Option_Type'].str.lower() == 'put') & (options_df['Absolute_Percentage_Error'] != float('inf'))]

    if not call_options_df.empty:
        average_call_error = call_options_df['Absolute_Percentage_Error'].mean()
        print(f"  Average Absolute Error (Call Options): {average_call_error:.2f}%")
    else:
        print("  No valid Call Options data to calculate average error.")

    if not put_options_df.empty:
        average_put_error = put_options_df['Absolute_Percentage_Error'].mean()
        print(f"  Average Absolute Error (Put Options):  {average_put_error:.2f}%")
    else:
         print("  No valid Put Options data to calculate average error.")
    median_absolute_error = options_df[options_df['Absolute_Percentage_Error'] != float('inf')]['Absolute_Percentage_Error'].median()
    std_dev_error = options_df[options_df['Percentage_Error'] != float('inf')]['Percentage_Error'].std()
    mean_error = options_df[options_df['Percentage_Error'] != float('inf')]['Percentage_Error'].mean()


    if not pd.isna(median_absolute_error):
         print(f"  Median Absolute Error:      {median_absolute_error:.2f}%")
    else:
        print("  Median Absolute Error:      Could not be calculated.")

    if not pd.isna(std_dev_error):
        print(f"  Standard Deviation of Error: {std_dev_error:.2f}%")
    else:
        print(" Could not be calculated.")

    if not pd.isna(mean_error):
        print(f"  Mean Error:                 {mean_error:.2f}%")
    else:
        print("  Could not be calculated.")


    print("="*55)
else:
    print("No data available in 'options_df' to provide a summary.")
