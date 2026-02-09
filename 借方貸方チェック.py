
def check_balance(debit_list, credit_list):
    """
    借方(debit)と貸方(credit)の合計が一致するかチェックする
    """
    sum_debit = sum(debit_list)
    sum_credit = sum(credit_list)
    
    if sum_debit == sum_credit:
        return "一致：仕訳は正常です。"
    else:
        # ここで設定したエラーコードを使ってみましょう
        return "エラーⅠ；振替不可（金額が一致しません）"

#試してみる
debit_amounts = [1000, 500]  # 借方：現金 1000, 売上 500
credit_amounts = [1500]      # 貸方：買掛金 1500

result = check_balance(debit_amounts, credit_amounts)
print(result)
