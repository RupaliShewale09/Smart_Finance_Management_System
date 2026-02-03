import joblib
import pandas as pd

# 1. Load files
try:
    model = joblib.load('ML model/Expense Categorization/Expense_categorization.pkl')
    le_merchant = joblib.load('ML model/Expense Categorization/merchant_name_encoder.pkl')
    le_category = joblib.load('ML model/Expense Categorization/merchant_category_encoder.pkl')
    print("✅ Model aur Encoders load successfully!\n")
except Exception as e:
    print(f"❌ Error loading files: {e}")
    exit()

# 2. Reverse Mappings 
category_map_inv = {2: 'Red (Critical)', 1: 'Orange (Necessary)', 0: 'Yellow (Discretionary)'}

def predict_expense(merchant, m_category, amount, is_recurring, balance, hour, day_of_week):
    try:
        # A. Label Encoding 
        try:
            m_encoded = le_merchant.transform([merchant])[0]
        except:
            m_encoded = 0 # Default/Unknown category handle

        try:
            cat_encoded = le_category.transform([m_category])[0]
        except:
            cat_encoded = 0 # Default for unknown category

        # B. Feature Array
        feature_data = [[m_encoded, cat_encoded, amount, int(is_recurring), balance, hour, day_of_week]]
        cols = ['merchant_name', 'merchant_category', 'amount', 'is_recurring', 'user_balance_pre', 'hour', 'day_of_week']
        input_df = pd.DataFrame(feature_data, columns=cols)


        # C. Prediction
        prediction = model.predict(input_df)[0]
        return category_map_inv[prediction]
    
    except Exception as e:
        return f"Error in prediction: {e}"

# --- TEST EXAMPLES ---

print("--- Testing Indian Transactions with Categories ---")

# Example 1: Electricity Bill (Critical)
res1 = predict_expense("BSESRAJASTHAN@HDFC", "Utilities", 3500, False, 1000, 10, 1)
print(f"\n1. Electricity Bill (₹3500): {res1}")

# Example 2: Zomato Food Order (Discretionary)
res2 = predict_expense("UPI-ZOMATO-PAYMENTS@HDFC", "Food & Dining", 450, False, 5000, 21, 3)
print(f"\n2. Zomato Dinner (₹450): {res2}")

# Example 3: Grocery (Necessary)
res3 = predict_expense("Suresh Kirana", "Groceries", 200, False, 2000, 9, 1)
print(f"\n3. Local Kirana (₹200): {res3}")

# Example 4: Insurance (Critical)
res4 = predict_expense("LIC Premium Payment", "Insurance", 15000, False, 25000, 11, 0)
print(f"\n4. LIC Insurance (₹15,000): {res4}")

# Example 5: Subscription (Discretionary)
res5 = predict_expense("VPA-Netflix@PAYTM", "Entertainment", 199, True, 4500, 10, 1)
print(f"\n5. Netflix Subscription (₹199): {res5}")

# Example 6: Petrol (Necessary)
res6 = predict_expense("HP Petrol Pump", "Fuel", 2000, False, 8000, 18, 5)
print(f"\n6. Petrol Refill (₹2,000): {res6}")

# Example 7: Home Loan (Critical)
res9 = predict_expense("HDFC Home Loan", "Debt Repayment", 45000, False, 60000, 9, 1)
print(f"\n9. Home Loan EMI (₹45,000): {res9}")
