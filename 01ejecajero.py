from datetime import datetime
from math import isfinite


# Defino errores específicos para las operaciones del banco.
class SaldoInsuficiente(Exception):
    pass


class CuentaNoExiste(Exception):
    pass


class LimiteRetiradaSuperado(Exception):
    pass


class Movimiento:
    def __init__(self, concepto, importe):
        # Guardo los datos como privados.
        self.__fecha = datetime.now()
        self.__concepto = concepto
        self.__importe = importe

    def __str__(self):
        # Indico cómo se muestra un movimiento al imprimirlo.
        return (
            f"{self.__fecha:%d/%m/%Y %H:%M:%S} | "
            f"{self.__concepto:<20} | "
            f"{self.__importe:>8.2f} €"
        )


class Cuenta:
    def __init__(self, numero, titular, saldo, limite_retirada=1000):
        # Compruebo que los valores iniciales sean válidos.
        if not isfinite(saldo) or saldo < 0:
            raise ValueError("El saldo inicial debe ser finito y no negativo.")

        if not isfinite(limite_retirada) or limite_retirada <= 0:
            raise ValueError("El límite debe ser finito y mayor que cero.")

        # Encapsulo los atributos para controlar su modificación.
        self.__numero = numero
        self.__titular = titular
        self.__saldo = saldo
        self.__movimientos = []

        # Acumulo las retiradas durante la ejecución del programa.
        self.__limite_retirada = limite_retirada
        self.__retirado = 0

    # Las propiedades permiten consultar los datos.
    # Al no definir setters, no permiten asignarles valores directamente.
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
    def disponible_retirada(self):
        # Calculo cuánto queda del límite de retirada.
        return self.__limite_retirada - self.__retirado

    def __validar_cantidad(self, cantidad):
        # Este método privado comprueba los importes.
        if not isfinite(cantidad) or cantidad <= 0:
            raise ValueError("La cantidad debe ser finita y mayor que cero.")

    def ingresar(self, cantidad):
        self.__validar_cantidad(cantidad)

        # Aumento el saldo y registro el ingreso.
        self.__saldo += cantidad
        self.__movimientos.append(
            Movimiento("Ingreso", cantidad)
        )

    def retirar(self, cantidad):
        self.__validar_cantidad(cantidad)

        # Compruebo el saldo antes de modificar la cuenta.
        if cantidad > self.__saldo:
            raise SaldoInsuficiente("Saldo insuficiente.")

        # Compruebo el total acumulado, no solo esta retirada.
        if cantidad > self.disponible_retirada:
            raise LimiteRetiradaSuperado(
                f"Has superado el límite de retirada. "
                f"Puedes retirar como máximo "
                f"{self.disponible_retirada:.2f} € más."
            )

        # Solo actualizo los datos si se cumplen las condiciones.
        self.__saldo -= cantidad
        self.__retirado += cantidad

        self.__movimientos.append(
            Movimiento("Retirada", -cantidad)
        )

    def transferir(self, destino, cantidad):
        self.__validar_cantidad(cantidad)

        if not isinstance(destino, Cuenta):
            raise ValueError("El destino debe ser una cuenta.")

        if destino is self:
            raise ValueError("No puedes transferir a la misma cuenta.")

        if cantidad > self.__saldo:
            raise SaldoInsuficiente("Saldo insuficiente.")

        # Una transferencia mueve dinero entre dos cuentas.
        # No cuenta como retirada de efectivo.
        self.__saldo -= cantidad
        destino.__saldo += cantidad

        # Dentro de Cuenta puedo acceder a los atributos privados de otra instancia de la misma clase.
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
        # Muestro la información sin exponer la lista interna.
        if not self.__movimientos:
            print("\nNo hay movimientos.")
            return

        print("\n--- MOVIMIENTOS ---")

        for movimiento in self.__movimientos:
            print(movimiento)


class Banco:
    def __init__(self):
        # Guardo las cuentas en un diccionario privado.
        self.__cuentas = {}

    def agregar_cuenta(self, cuenta):
        # Evito sobrescribir una cuenta que ya existe.
        if cuenta.numero in self.__cuentas:
            raise ValueError("Ya existe una cuenta con ese número.")

        self.__cuentas[cuenta.numero] = cuenta

    def buscar_cuenta(self, numero):
        if numero not in self.__cuentas:
            raise CuentaNoExiste("Cuenta no encontrada.")

        return self.__cuentas[numero]


def menu_cuenta(cuenta, banco):
    # Repito el menú hasta que el usuario cierre sesión.
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
                print(f"\nSaldo actual: {cuenta.saldo:.2f} €")
                print(
                    f"Disponible para retirar en esta ejecución: "
                    f"{cuenta.disponible_retirada:.2f} €"
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
                # Salgo del menú sin reiniciar las retiradas acumuladas.
                break

            else:
                print("Opción incorrecta.")

        except (
            SaldoInsuficiente,
            CuentaNoExiste,
            LimiteRetiradaSuperado,
            ValueError
        ) as e:
            # Muestro el error y permito seguir usando el cajero.
            print("Error:", e)


# =====================
# PROGRAMA PRINCIPAL
# =====================

if __name__ == "__main__":
    # Creo el banco y añado tres cuentas de ejemplo.
    banco = Banco()

    banco.agregar_cuenta(Cuenta("1001", "Sara", 2500))
    banco.agregar_cuenta(Cuenta("1002", "Luis", 1500))
    banco.agregar_cuenta(Cuenta("1003", "Ana", 3000))

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