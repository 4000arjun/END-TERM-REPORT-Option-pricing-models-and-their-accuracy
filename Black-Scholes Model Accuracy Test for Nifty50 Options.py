import numpy as np
import pandas as pd
from scipy.stats import norm
from datetime import datetime

# --- Black-Scholes Model Implementation ---

def black_scholes(S, K, T, r, sigma, option_type='call'):
    """
    Calculates the Black-Scholes option price for a call or put.

    Parameters:
    - S (float): Current price of the underlying asset (e.g., Nifty50 index).
    - K (float): Strike price of the option.
    - T (float): Time to expiration in years.
    - r (float): Risk-free interest rate (annualized).
    - sigma (float): Volatility of the underlying asset's returns (annualized).
    - option_type (str): Type of the option, either 'call' or 'put'.

    Returns:
    - float: The theoretical price of the option.
    """
    # Handle cases where T is zero or negative to avoid division by zero
    if T <= 0:
        # If time to expiration is zero, the option value is its intrinsic value
        if option_type.lower() == 'call':
            return max(0.0, S - K)
        elif option_type.lower() == 'put':
            return max(0.0, K - S)
        else:
            return 0.0

    # Calculate d1 and d2
    # Ensure S, K, T, r, and sigma are numerical types
    S = float(S)
    K = float(K)
    T = float(T)
    r = float(r)
    sigma = float(sigma)

    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    if option_type.lower() == 'call':
        # Calculate call option price using the Black-Scholes formula
        option_price = (S * norm.cdf(d1, 0.0, 1.0) - K * np.exp(-r * T) * norm.cdf(d2, 0.0, 1.0))
    elif option_type.lower() == 'put':
        # Calculate put option price using the Black-Scholes formula
        option_price = (K * np.exp(-r * T) * norm.cdf(-d2, 0.0, 1.0) - S * norm.cdf(-d1, 0.0, 1.0))
    else:
        raise ValueError("Invalid option type. Please choose 'call' or 'put'.")

    return option_price

# --- Main Execution: Assess Model Accuracy from CSV ---

if __name__ == "__main__":
    
    CSV_FILE_NAME = 'nifty_options_data (final 2).csv'

    # --- 2. LOAD AND PROCESS DATA FROM CSV ---
    try:
        # Read the CSV with the identified encoding
        options_df = pd.read_csv(CSV_FILE_NAME, encoding='cp1252')

        # Clean up column names by stripping whitespace
        options_df.columns = options_df.columns.str.strip()

        # Correct specific column name typos/issues after stripping whitespace
        options_df.rename(columns={'Option_Typut': 'Option_Type', 'Nifty_Close': 'Nifty_Close'}, inplace=True)


        # Now parse the date columns after cleaning the names
        options_df['Date'] = pd.to_datetime(options_df['Date'], errors='coerce')
        options_df['Expiry_Date'] = pd.to_datetime(options_df['Expiry_Date'], errors='coerce')

        # Convert key numerical columns to numeric, coercing errors to NaN
        options_df['Nifty_Close'] = pd.to_numeric(options_df['Nifty_Close'], errors='coerce')
        options_df['Strike_Price'] = pd.to_numeric(options_df['Strike_Price'], errors='coerce')
        options_df['Option_Close'] = pd.to_numeric(options_df['Option_Close'], errors='coerce')

        # Drop rows where date parsing failed or key numerical data is missing
        options_df.dropna(subset=['Date', 'Expiry_Date', 'Nifty_Close', 'Strike_Price', 'Option_Close', 'Option_Type'], inplace=True)


    except FileNotFoundError:
        print(f"Error: '{CSV_FILE_NAME}' not found.")
        print("Please create the CSV file with the required data and place it in the same directory.")
        # Removed the exit() call here
    except KeyError as e:
        print(f"Error: Missing expected column after cleaning: {e}")
    except Exception as e:
        print(f"An error occurred during file reading or initial processing: {e}")


    # Calculate Time to Expiration (T) as a column
    if 'Date' in options_df.columns and 'Expiry_Date' in options_df.columns:
        options_df['Time_to_Expiration_Days'] = (options_df['Expiry_Date'] - options_df['Date']).dt.days
        options_df['T'] = options_df['Time_to_Expiration_Days'] / 365.0

        # Set constant parameters for the model (could be columns in a more advanced model)
        r = 0.0685  # Constant risk-free rate
        sigma = 0.1450 # Constant historical volatility

        # Calculate Black-Scholes price for each row using apply (less efficient for large data)
        # or a vectorized approach if possible for the black_scholes function
        # For simplicity and matching the original loop structure, we'll use apply
        options_df['Black_Scholes_Price'] = options_df.apply(
            lambda row: black_scholes(
                row['Nifty_Close'],
                row['Strike_Price'],
                row['T'],
                r,
                sigma,
                row['Option_Type']
            ),
            axis=1
        )

        # Calculate pricing error and percentage error
        options_df['Pricing_Error'] = options_df['Black_Scholes_Price'] - options_df['Option_Close']
        # Handle division by zero for percentage error where Option_Close is 0
        options_df['Percentage_Error'] = options_df.apply(
            lambda row: (row['Pricing_Error'] / row['Option_Close']) * 100 if row['Option_Close'] != 0 else float('inf'),
            axis=1
        )
        options_df['Absolute_Percentage_Error'] = options_df['Percentage_Error'].abs()

        print(f"--- Starting Black-Scholes Accuracy Test on data from '{CSV_FILE_NAME}' ---")

        # Print results for each option (similar to the original loop)
        for index, row in options_df.iterrows():
            print(f"\n--- Processing Option: {row['Date'].strftime('%Y-%m-%d')} | {row['Strike_Price']} {row['Option_Type'].upper()} ---")
            print(f"  Actual Market Price:       ₹{row['Option_Close']:.2f}")
            print(f"  Black-Scholes Price:       ₹{row['Black_Scholes_Price']:.2f}")
            # Check for infinite percentage error before printing
            if row['Percentage_Error'] == float('inf'):
                 print(f"  Pricing Difference:        ₹{row['Pricing_Error']:.2f} (Infinite %)")
            else:
                 print(f"  Pricing Difference:        ₹{row['Pricing_Error']:.2f} ({row['Percentage_Error']:.2f}%)")


        # --- 5. FINAL SUMMARY ---
        processed_rows = len(options_df) # Now processed_rows is the number of valid rows
        if processed_rows > 0:
            # Calculate overall average absolute error from the column
            average_error = options_df[options_df['Absolute_Percentage_Error'] != float('inf')]['Absolute_Percentage_Error'].mean()

            print("\n" + "="*55)
            print("                      OVERALL SUMMARY")
            print("="*55)
            print(f"  Total Options Processed:    {processed_rows}")
            print(f"  Average Absolute Error:     {average_error:.2f}%")
            print("="*55)
        else:
            print("\nNo valid options data found to process in the CSV file.")
    else:
         print("\nDate or Expiry_Date columns not found or processed correctly. Cannot calculate time to expiration.")
