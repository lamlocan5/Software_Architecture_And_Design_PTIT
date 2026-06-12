import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal

db_host = 'localhost'
db_port = '5432'
db_user = 'postgres'
db_password = '1234'

try:
    import psycopg2
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
    import psycopg2

def connect_db(db_name):
    return psycopg2.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        database=db_name
    )

def feed_doctors():
    print("Feeding healthcare_doctor...")
    conn = connect_db("healthcare_doctor")
    cursor = conn.cursor()
    
    cursor.execute("TRUNCATE TABLE doctors RESTART IDENTITY CASCADE;")
    
    doctors = [
        ("Bác sĩ Nguyễn Văn An", "Tai Mũi Họng", "0911223344", "annv@healthcare.com"),
        ("Bác sĩ Trần Thị Bình", "Tim Mạch", "0922334455", "binhtt@healthcare.com"),
        ("Bác sĩ Lê Hoàng Nam", "Tiêu Hóa", "0933445566", "namlh@healthcare.com"),
        ("Bác sĩ Phạm Minh Thư", "Truyền Nhiễm", "0944556677", "thupm@healthcare.com")
    ]
    
    for name, specialty, phone, email in doctors:
        cursor.execute(
            """INSERT INTO doctors (full_name, specialty, phone, email, created_at, updated_at) 
               VALUES (%s, %s, %s, %s, NOW(), NOW());""",
            (name, specialty, phone, email)
        )
        
    conn.commit()
    cursor.close()
    conn.close()
    print("healthcare_doctor fed successfully!")

def feed_patients():
    print("Feeding healthcare_patient...")
    conn = connect_db("healthcare_patient")
    cursor = conn.cursor()
    
    cursor.execute("TRUNCATE TABLE patients RESTART IDENTITY CASCADE;")
    
    patients = [
        ("Nguyễn Văn Hùng", "1980-05-12", "male", "0901234567", "hungnv@gmail.com", "123 Đường Láng, Hà Nội"),
        ("Trần Thị Lan", "1992-09-24", "female", "0987654321", "lantt@yahoo.com", "456 Nguyễn Thị Minh Khai, TP.HCM"),
        ("Phạm Minh Đức", "1975-02-18", "male", "0912345678", "ducpm@outlook.com", "789 Lê Lợi, Đà Nẵng"),
        ("Lê Thị Hồng", "1988-11-05", "female", "0934567890", "hongle@gmail.com", "12 Trần Hưng Đạo, Cần Thơ"),
        ("Hoàng Anh Tuấn", "2000-07-30", "male", "0945678901", "tuanha@gmail.com", "55 Hùng Vương, Huế")
    ]
    
    for name, dob, gender, phone, email, addr in patients:
        cursor.execute(
            """INSERT INTO patients (full_name, date_of_birth, gender, phone, email, address, created_at, updated_at) 
               VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW());""",
            (name, dob, gender, phone, email, addr)
        )
        
    conn.commit()
    cursor.close()
    conn.close()
    print("healthcare_patient fed successfully!")

def feed_clinical_and_billing():
    print("Feeding healthcare_clinical & healthcare_billing...")
    
    # Connect to both databases
    conn_clinical = connect_db("healthcare_clinical")
    cursor_clinical = conn_clinical.cursor()
    
    conn_billing = connect_db("healthcare_billing")
    cursor_billing = conn_billing.cursor()
    
    # 1. Clear existing data
    cursor_clinical.execute("TRUNCATE TABLE prescription_items, prescriptions, appointments RESTART IDENTITY CASCADE;")
    cursor_billing.execute("TRUNCATE TABLE bill_items, bills RESTART IDENTITY CASCADE;")
    
    # 2. Seed Appointments & Prescriptions for patient_ids 1 to 4
    appointments = [
        # (patient_id, doctor_id, scheduled_offset_days, status, notes)
        (1, 1, -3, "completed", "Bệnh nhân đau họng nhẹ, ho khan."),
        (2, 2, -2, "completed", "Khám định kỳ, huyết áp hơi cao."),
        (3, 3, -1, "completed", "Đau dạ dày sau khi ăn đồ cay nóng."),
        (4, 4, 1, "confirmed", "Tái khám kiểm tra tình trạng sốt xuất huyết.")
    ]
    
    for index, (patient_id, doctor_id, offset, status, notes) in enumerate(appointments, start=1):
        scheduled_time = datetime.now() + timedelta(days=offset)
        
        # Insert Appointment
        cursor_clinical.execute(
            """INSERT INTO appointments (patient_id, doctor_id, scheduled_at, status, notes, created_at) 
               VALUES (%s, %s, %s, %s, %s, NOW()) RETURNING id;""",
            (patient_id, doctor_id, scheduled_time, status, notes)
        )
        appt_id = cursor_clinical.fetchone()[0]
        
        # If completed, create Prescription & Bill
        if status == "completed":
            diagnosis = f"Chẩn đoán cho lịch hẹn #{appt_id}: " + ("Viêm họng cấp" if index == 1 else "Huyết áp cao độ 1" if index == 2 else "Viêm dạ dày nhẹ")
            
            # Insert Prescription
            cursor_clinical.execute(
                """INSERT INTO prescriptions (appointment_id, patient_id, diagnosis, created_at) 
                   VALUES (%s, %s, %s, NOW()) RETURNING id;""",
                (appt_id, patient_id, diagnosis)
            )
            presc_id = cursor_clinical.fetchone()[0]
            
            # Insert Prescription Items
            items = []
            if index == 1:
                items = [("Amoxicillin 500mg", 20, "Uống 2 viên/ngày chia 2 lần sau ăn"), ("Paracetamol 500mg", 10, "Uống 1 viên khi sốt > 38.5 độ")]
            elif index == 2:
                items = [("Amlodipine 5mg", 30, "Uống 1 viên vào buổi sáng")]
            elif index == 3:
                items = [("Omeprazole 20mg", 14, "Uống 1 viên trước ăn sáng 30 phút")]
                
            for med_name, qty, dosage in items:
                cursor_clinical.execute(
                    """INSERT INTO prescription_items (prescription_id, medicine_name, quantity, dosage) 
                       VALUES (%s, %s, %s, %s);""",
                    (presc_id, med_name, qty, dosage)
                )
            
            # Insert Bill
            total_amount = Decimal("150000.00") # Khám lâm sàng
            med_cost = Decimal("0.00")
            
            bill_items = [("Công khám lâm sàng", Decimal("150000.00"), 1)]
            for med_name, qty, _ in items:
                price = Decimal("2000.00")
                if "Amoxicillin" in med_name: price = Decimal("5000.00")
                elif "Amlodipine" in med_name: price = Decimal("6000.00")
                elif "Omeprazole" in med_name: price = Decimal("8000.00")
                cost = price * qty
                med_cost += cost
                bill_items.append((med_name, price, qty))
                
            total_amount += med_cost
            
            # Create Bill
            bill_status = "paid" if index <= 2 else "pending"
            paid_time = datetime.now() - timedelta(days=1) if bill_status == "paid" else None
            
            cursor_billing.execute(
                """INSERT INTO bills (patient_id, prescription_id, total_amount, status, created_at, paid_at) 
                   VALUES (%s, %s, %s, %s, NOW(), %s) RETURNING id;""",
                (patient_id, presc_id, total_amount, bill_status, paid_time)
            )
            bill_id = cursor_billing.fetchone()[0]
            
            for desc, price, qty in bill_items:
                cursor_billing.execute(
                    """INSERT INTO bill_items (bill_id, description, unit_price, quantity) 
                       VALUES (%s, %s, %s, %s);""",
                    (bill_id, desc, price, qty)
                )
                
    conn_clinical.commit()
    conn_billing.commit()
    
    cursor_clinical.close()
    conn_clinical.close()
    
    cursor_billing.close()
    conn_billing.close()
    print("healthcare_clinical and healthcare_billing fed successfully!")

def feed_inventory():
    print("Feeding healthcare_inventory...")
    conn = connect_db("healthcare_inventory")
    cursor = conn.cursor()
    
    cursor.execute("TRUNCATE TABLE stock_transactions, medicines RESTART IDENTITY CASCADE;")
    
    medicines = [
        ("Paracetamol 500mg", "viên", 1000, 2000.00),
        ("Amoxicillin 500mg", "viên", 500, 5000.00),
        ("Omeprazole 20mg", "viên", 400, 8000.00),
        ("Metformin 500mg", "viên", 600, 3000.00),
        ("Amlodipine 5mg", "viên", 300, 6000.00),
        ("Azithromycin 250mg", "viên", 200, 12000.00),
        ("Ibuprofen 400mg", "viên", 500, 4000.00),
        ("Vitamin C 1000mg", "viên", 800, 2500.00),
        ("Loratadine 10mg", "viên", 350, 5000.00),
        ("Betadine 10% 90ml", "chai", 100, 45000.00)
    ]
    
    med_ids = {}
    for name, unit, stock, price in medicines:
        cursor.execute(
            """INSERT INTO medicines (name, unit, stock, unit_price, updated_at) 
               VALUES (%s, %s, %s, %s, NOW()) RETURNING id;""",
            (name, unit, stock, price)
        )
        med_id = cursor.fetchone()[0]
        med_ids[name] = med_id
        
    # Create some import transactions
    for name, med_id in med_ids.items():
        qty = 1000 if "Betadine" not in name else 100
        cursor.execute(
            """INSERT INTO stock_transactions (medicine_id, transaction_type, quantity, reference_id, created_at) 
               VALUES (%s, 'import', %s, 'INITIAL_IMPORT', NOW());""",
            (med_id, qty)
        )
        
    conn.commit()
    cursor.close()
    conn.close()
    print("healthcare_inventory fed successfully!")

if __name__ == "__main__":
    try:
        feed_doctors()
        feed_patients()
        feed_clinical_and_billing()
        feed_inventory()
        print("\nAll database feeds executed successfully!")
    except Exception as e:
        print(f"Error during seeding: {e}")
        sys.exit(1)
