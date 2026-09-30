from datetime import datetime


class SaldoInsuficiente(Exception):
    pass


class CuentaNoExiste(Exception):
    pass


class Movimiento:
    def __init__(self, concepto, importe):
        self.fecha = datetime.now()
        self.concepto = concepto
        self.importe = importe

    def __str__(self):
        return (
            f"{self.fecha:%d/%m/%Y %H:%M:%S} | "
            f"{self.concepto:<20} | "
            f"{self.importe:>8.2f} €"
        )


class Cuenta:
    def __init__(self, numero, titular, saldo):
        self.numero = numero
        self.titular = titular
        self.saldo = saldo
        self.movimientos = []

    def ingresar(self, cantidad):
        self.saldo += cantidad
        self.movimientos.append(
            Movimiento("Ingreso", cantidad)
        )

    def retirar(self, cantidad):
        if cantidad > self.saldo:
            raise SaldoInsuficiente("Saldo insuficiente")

        self.saldo -= cantidad
        self.movimientos.append(
            Movimiento("Retirada", -cantidad)
        )

    def transferir(self, destino, cantidad):
        if cantidad > self.saldo:
            raise SaldoInsuficiente("Saldo insuficiente")

        self.saldo -= cantidad
        destino.saldo += cantidad

        self.movimientos.append(
            Movimiento(f"Transferencia a {destino.numero}", -cantidad)
        )

        destino.movimientos.append(
            Movimiento(f"Transferencia de {self.numero}", cantidad)
        )

    def mostrar_movimientos(self):
        if not self.movimientos:
            print("\nNo hay movimientos.")
            return

        print("\n--- MOVIMIENTOS ---")

        for movimiento in self.movimientos:
            print(movimiento)


class Banco:
    def __init__(self):
        self.cuentas = {}

    def agregar_cuenta(self, cuenta):
        self.cuentas[cuenta.numero] = cuenta

    def buscar_cuenta(self, numero):
        if numero not in self.cuentas:
            raise CuentaNoExiste("Cuenta no encontrada")

        return self.cuentas[numero]


def menu_cuenta(cuenta, banco):
    while True:
        print(f"\n=== CAJERO ({cuenta.titular}) ===")
        print("1. Consultar saldo")
        print("2. Ingresar dinero")
        print("3. Retirar dinero")
        print("4. Transferencia")
        print("5. Ver movimientos")
        print("6. Cerrar sesión")

        opcion = input("Opción: ")

        try:
            if opcion == "1":
                print(
                    f"\nSaldo actual: "
                    f"{cuenta.saldo:.2f} €"
                )

            elif opcion == "2":
                cantidad = float(input("Cantidad: "))
                cuenta.ingresar(cantidad)
                print("Ingreso realizado.")

            elif opcion == "3":
                cantidad = float(input("Cantidad: "))
                cuenta.retirar(cantidad)
                print("Retirada realizada.")

            elif opcion == "4":
                destino_num = input("Cuenta destino: ")
                cantidad = float(input("Cantidad: "))

                destino = banco.buscar_cuenta(destino_num)
                cuenta.transferir(destino, cantidad)

                print("Transferencia realizada.")

            elif opcion == "5":
                cuenta.mostrar_movimientos()

            elif opcion == "6":
                break

            else:
                print("Opción incorrecta.")

        except Exception as e:
            print("Error:", e)


# =====================
# PROGRAMA PRINCIPAL
# =====================

banco = Banco()

banco.agregar_cuenta(
    Cuenta("1001", "Sara", 2500)
)

banco.agregar_cuenta(
    Cuenta("1002", "Luis", 1500)
)

banco.agregar_cuenta(
    Cuenta("1003", "Ana", 3000)
)

while True:
    print("\n=== BANCO PYTHON ===")
    print("1. Acceder a cuenta")
    print("2. Salir")

    opcion = input("Opción: ")

    if opcion == "1":
        numero = input("Número de cuenta: ")

        try:
            cuenta = banco.buscar_cuenta(numero)
            menu_cuenta(cuenta, banco)

        except Exception as e:
            print("Error:", e)

    elif opcion == "2":
        print("Hasta pronto.")
        break

    else:
        print("Opción inválida.")