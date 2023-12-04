************************************************************პროექტი**********************************************
import pandas as pd
import matplotlib.pyplot as plt
import pymongo


class invoice:
    """ინვოისის კლასი"""

    def __init__(self, invoice_no, description, quantity, invoice_date, unit_price, customer_id, country,file_name):
        """ატრიბუტების ინიციალიზაცია"""
        self.invoice_no = invoice_no
        self.description = description
        self.quantity = quantity
        self.invoice_date = invoice_date
        self.unit_price = unit_price
        self.customer_id = customer_id
        self.country = country
        self.file_name = file_name

    def read_data(self):
        # წაკითხვა ექსელიდან
        df = pd.read_excel(self.file_name)
        return df

    def calculate_total(self):
        total_cost = self['Quantity'] * self['UnitPrice']
        return total_cost.sum()


class Specialinvoice(invoice):
    """დამატებით ატრიბუტით კლასი ამ შემთხვევაში ფასდაკლება"""

    def __init__(self, invoice_no, description, quantity, invoice_date, unit_price, customer_id, country, file_name,discount):
        super().__init__(invoice_no, description, quantity, invoice_date, unit_price, customer_id, country,file_name)
        self.discount = discount

    def calculate_total(self):
        """ფასდაკების დამატება"""
        return super().calculate_total() * (1 - self.discount)


class DataProcessor:
    """მონაცემთა დამუშავება პანდას გამოყენებით"""

    def read_data(self, file_name):
        """წაკითხვა ფაილას რომელსაც გადავცემთ ."""
        df = pd.read_excel(file_name)
        return df

    def clean_data(self, df):
        """გასაუფთავება ცარიელი მწკრივის"""
        df.dropna(inplace=True)
        #სვეტში ინვოისის დრო დროის ტიპზე გადაგვყავს
        df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
        return df

    def transform_data(self, df):
        """მონაცემთა ჩასაწერად """
        # მთლიანი თანხის გამოთვლა თვითოეულ ინვოისზე
        df['TotalCost'] = df.apply(lambda row: row['Quantity'] * row['UnitPrice'], axis=1)
        return df

def store_data(df, database):
        """მონგოს მონაცემთა ბსაზაში შეტვირთვა"""
        # მონაცემთა ბაზის წამოღება
        client = pymongo.MongoClient(database)
        db = client.invoices  # ამოიღო ინვოისები ბაზიდან
        invoices_collection = db.invoices  # ინვოისების კოლექციის ამოღება
        # ლექსიკონის მწკრივებად გარდაქმნა
        invoices = df.to_dict('records')
        # შეყვანა ინვოისების კოლექციაში
        invoices_collection.insert_many(invoices)
        # დახურვა
        client.close()


def visualize_data(df):
    """ვიზუალიზაცია Matplotlib ში"""
    # გამოთვლა თვითოეული ქვეყნის მთლიანი გაყიდვების
    sales_by_country = df.groupby('Country')['TotalCost'].sum().reset_index()

    plt.bar(sales_by_country['Country'], sales_by_country['TotalCost'])
    plt.xlabel('ქვეყანა')
    plt.ylabel('მთლიანი გაყიდვები')
    plt.title('გაყიდვები ქვეყნების მიხედვით')
    plt.show()
    #  მომხარებლის ნაყიდი რაოდენობა
    CustomerID_by_quantity = df[['CustomerID', 'Quantity']]

    CustomerID_by_quantity = CustomerID_by_quantity.groupby('CustomerID').sum()
    CustomerID_by_quantity.plot(kind='barh',  color='red')
    plt.show()

def main():

    invoice_data = invoice(invoice_no=123, description='Sacivi', quantity=100, invoice_date='2023-01-01', unit_price=100,
                           customer_id=1, country='georgia', file_name='sample_data.xlsx').read_data()


    total_cost = invoice.calculate_total(invoice_data)
    print('მთლიანი თანხა= ',total_cost)


    print(invoice_data.to_string())


    try:
        # წაიკითხა მონაცემების კლასიდან
        processor = DataProcessor()
        df = processor.read_data('sample_data.xlsx')
        #
        df = processor.clean_data(df)
        df = processor.transform_data(df)
        # ვიზუალიზაცია
        visualize_data(df)
        # შენახმვა მონაცემთა ბაზაში
        store_data(df,'mongodb://localhost:27017/invoices')


    except Exception as e:
        print(f'Error: {e}')


if __name__ == '__main__':
    main()