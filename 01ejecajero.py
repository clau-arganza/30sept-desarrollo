from datetime import datetime


class SaldoInsuficiente(Exception):
    pass


class CuentaNoExiste(Exception):
    pass


class Movimiento:
    def __init__(self, concepto, importe):
        # Encapsulo los atributos del movimiento.
        self.__fecha = datetime.now()
        self.__concepto = concepto
        self.__importe = importe

    # Estas propiedades permiten consultar los datos.
    @property
    def fecha(self):
        return self.__fecha

    @property
    def concepto(self):
        return self.__concepto

    @property
    def importe(self):
        return self.__importe

    def __str__(self):
        return (
            f"{self.__fecha:%d/%m/%Y %H:%M:%S} | "
            f"{self.__concepto:<20} | "
            f"{self.__importe:>8.2f} €"
        )


class Cuenta:
    def __init__(self, numero, titular, saldo):
        if saldo < 0:
            raise ValueError("El saldo inicial no puede ser negativo.")

        # Los atributos se gestionan desde los métodos de la clase.
        self.__numero = numero
        self.__titular = titular
        self.__saldo = saldo
        self.__movimientos = []

    @property
    def numero(self):
        return self.__numero

    @property
    def titular(self):
        return self.__titular

    @property
    def saldo(self):
        return self.__saldo

    @property
    def movimientos(self):
        # Devuelvo una tupla para no exponer la lista interna.
        return tuple(self.__movimientos)

    def __validar_cantidad(self, cantidad):
        # Compruebo que el importe sea positivo.
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor que cero.")

    def ingresar(self, cantidad):
        self.__validar_cantidad(cantidad)

        self.__saldo += cantidad
        self.__movimientos.append(
            Movimiento("Ingreso", cantidad)
        )

    def retirar(self, cantidad):
        self.__validar_cantidad(cantidad)

        if cantidad > self.__saldo:
            raise SaldoInsuficiente("Saldo insuficiente")

        self.__saldo -= cantidad
        self.__movimientos.append(
            Movimiento("Retirada", -cantidad)
        )

    def transferir(self, destino, cantidad):
        self.__validar_cantidad(cantidad)

        if not isinstance(destino, Cuenta):
            raise ValueError("El destino debe ser una cuenta.")

        if destino is self:
            raise ValueError(
                "No puedes transferir dinero a la misma cuenta."
            )

        if cantidad > self.__saldo:
            raise SaldoInsuficiente("Saldo insuficiente")

        # Desde la clase Cuenta puedo acceder a los atributos
        # privados de otra instancia de esta misma clase.
        self.__saldo -= cantidad
        destino.__saldo += cantidad

        self.__movimientos.append(
            Movimiento(
                f"Transferencia a {destino.numero}",
                -cantidad
            )
        )

        destino.__movimientos.append(
            Movimiento(
                f"Transferencia de {self.__numero}",
                cantidad
            )
        )

    def mostrar_movimientos(self):
        if not self.__movimientos:
            print("\nNo hay movimientos.")
            return

        print("\n--- MOVIMIENTOS ---")

        for movimiento in self.__movimientos:
            print(movimiento)


class Banco:
    def __init__(self):
        # Encapsulo el diccionario que almacena las cuentas.
        self.__cuentas = {}

    def agregar_cuenta(self, cuenta):
        if cuenta.numero in self.__cuentas:
            raise ValueError("Ya existe una cuenta con ese número.")

        self.__cuentas[cuenta.numero] = cuenta

    def buscar_cuenta(self, numero):
        if numero not in self.__cuentas:
            raise CuentaNoExiste("Cuenta no encontrada")

        return self.__cuentas[numero]


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
                # Consulto el saldo mediante su propiedad.
                print(f"\nSaldo actual: {cuenta.saldo:.2f} €")

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

        except (SaldoInsuficiente, CuentaNoExiste, ValueError) as e:
            print("Error:", e)


# =====================
# PROGRAMA PRINCIPAL
# =====================

if __name__ == "__main__":
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

            except CuentaNoExiste as e:
                print("Error:", e)

        elif opcion == "2":
            print("Hasta pronto.")
            break

        else:
            print("Opción inválida.")