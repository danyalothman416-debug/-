// Customer.java
public class Customer {
    private String id;
    private String name;
    private String phoneNumber;
    private double totalDebt;
    private String lastTransactionDate;

    public Customer(String id, String name, String phoneNumber, double totalDebt, String lastTransactionDate) {
        this.id = id;
        this.name = name;
        this.phoneNumber = phoneNumber;
        this.totalDebt = totalDebt;
        this.lastTransactionDate = lastTransactionDate;
    }

    // Getters
    public String getId() { return id; }
    public String getName() { return name; }
    public String getPhoneNumber() { return phone
