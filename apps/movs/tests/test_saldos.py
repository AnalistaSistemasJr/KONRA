from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.catalogos.models import Cuenta, Estacion, Rubro
from apps.movs.models import Registro_Movimientos, SaldoInicial, Tipo_movimiento
from apps.movs.saldos import saldo_de_caja, saldo_de_movimientos, totales_por
from apps.movs.saldos import SaldoInicialNoConfigurado

class SaldoDeMovimientosTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = get_user_model().objects.create_user(
            username="user1", password="prueba-123-xyz"
        )
        cls.estacion = Estacion.objects.create(
            numero_estacion=1, estacion="PUEBLITO", estacion_activa=True
        )
        cls.rubro = Rubro.objects.create(rubro="Sueldos")
        cls.cuenta = Cuenta.objects.create(
            numero_cuenta="40-00-00-00-00",
            nombre_cuenta="Ingresos",
            tipo_cuenta="Activos",
            rubro=cls.rubro,
            cuenta_activa=True,
        )

        cls.estacion2 = Estacion.objects.create(
            numero_estacion=2, estacion="MACIAS", estacion_activa=True
        )
        cls.cuenta2 = Cuenta.objects.create(
            numero_cuenta="50-00-00-00-00",
            nombre_cuenta="Efectivo",
            tipo_cuenta="Gastos",
            rubro=cls.rubro,
            cuenta_activa=True,
        )

    def _mov(self, tipo, monto, estacion = None, cuenta = None, fecha=None):
        return Registro_Movimientos.objects.create(
            fecha_caja=fecha or date(2026, 10, 1),
            estacion=estacion or self.estacion ,
            cuenta=cuenta or self.cuenta,
            tipo_movimiento=tipo,
            monto=Decimal(monto),
            descripcion="Prueba saldo",
            creado_por=self.usuario,
        )

    def test_entrada_positiva_suma(self):
        self._mov(Tipo_movimiento.ENTRADA, "200.00")
        self.assertEqual(saldo_de_movimientos(), Decimal("200.00"))

    def test_salida_positiva_resta(self):
        self._mov(Tipo_movimiento.SALIDA, "300.00")
        self.assertEqual(saldo_de_movimientos(), Decimal("-300.00"))

    def test_salida_negativa_suma(self):
        # Devolución: una Salida negativa SUMA al saldo.
        self._mov(Tipo_movimiento.SALIDA, "-50.00")
        self.assertEqual(saldo_de_movimientos(), Decimal("50.00"))

    def test_entrada_negativa_resta(self):
        self._mov(Tipo_movimiento.ENTRADA, "-30.00")
        self.assertEqual(saldo_de_movimientos(), Decimal("-30.00"))


    def test_saldo_de_caja_con_los_cuatro_movimientos(self):
        SaldoInicial.objects.create(
            monto=Decimal("1000.00"),
            fecha_referencia=date(2026, 10, 1),
            creado_por=self.usuario,
        )
        self._mov(Tipo_movimiento.ENTRADA, "200.00")
        self._mov(Tipo_movimiento.SALIDA, "300.00")
        self._mov(Tipo_movimiento.SALIDA, "-50.00")
        self._mov(Tipo_movimiento.ENTRADA, "-30.00")
        self.assertEqual(saldo_de_caja(), Decimal("920.00"))


    def test_sin_movimientos_devuelve_cero_decimal(self):
        resultado = saldo_de_movimientos()
        self.assertIsNotNone(resultado)
        self.assertIsInstance(resultado, Decimal)
        self.assertEqual(resultado, Decimal("0.00"))
        self.assertEqual(str(resultado), "0.00")


    def test_tres_movimientos_de_diez_centavos_suman_treinta(self):
        for _ in range(3):
            self._mov(Tipo_movimiento.ENTRADA, "0.10")
        resultado = saldo_de_movimientos()
        self.assertIsInstance(resultado, Decimal)
        self.assertEqual(resultado, Decimal("0.30"))
        self.assertEqual(str(resultado), "0.30")


    def test_saldo_de_caja_filtrado_fecha(self):
        self._mov(Tipo_movimiento.ENTRADA, "200", fecha="2026-10-01")
        self._mov(Tipo_movimiento.ENTRADA, "-100", fecha="2026-10-02")
        self._mov(Tipo_movimiento.SALIDA, "50", fecha="2026-10-03")

        resultado_filtrado = saldo_de_movimientos(hasta = "2026-10-02")
        resultado_completo = saldo_de_movimientos()
        self.assertEqual(resultado_filtrado, Decimal("100.00"))
        self.assertEqual(resultado_completo, Decimal("50.00"))


    def test_crear_movimientos_con_bulk_create(self):
        SaldoInicial.objects.create(
            monto=Decimal("1000.00"),
            fecha_referencia=date(2026, 10, 1),
            creado_por=self.usuario,
        )
        
        movimientos = []

        for i in range(25):
            movimientos.append(Registro_Movimientos(
                fecha_caja = date.today(),
                estacion = self.estacion,
                cuenta = self.cuenta,
                tipo_movimiento = Tipo_movimiento.ENTRADA,
                monto=Decimal("100.00"),
                descripcion="Prueba entrada bulk create",
                creado_por=self.usuario,                
            ))

        for i in range(25):
            movimientos.append(Registro_Movimientos(
                fecha_caja = date.today(),
                estacion = self.estacion,
                cuenta = self.cuenta,
                tipo_movimiento = Tipo_movimiento.SALIDA,
                monto=Decimal("50"),
                descripcion="Prueba salida bulk create",
                creado_por=self.usuario,                
            ))

        Registro_Movimientos.objects.bulk_create(movimientos)

        with self.assertNumQueries(1):
            saldo = saldo_de_movimientos()
        
        self.assertEqual(saldo, Decimal("1250.00"))

        with self.assertNumQueries(2):
            saldo_final = saldo_de_caja()
        
        self.assertEqual(saldo_final, Decimal("2250"))

    def test_registro_y_filtado_de_datos_por_campo_estacion(self):
        # Registros estación 1 ------------------
        self._mov(Tipo_movimiento.ENTRADA, "100")
        self._mov(Tipo_movimiento.ENTRADA, "100", cuenta = self.cuenta2)

        # Registros estación 2 ------------------
        self._mov(Tipo_movimiento.ENTRADA, "500", estacion = self.estacion2)
        self._mov(Tipo_movimiento.SALIDA, "-100", estacion = self.estacion2, cuenta=self.cuenta2)

        with self.assertNumQueries(1):
                resultado = totales_por("estacion")

        esperado = [
            {
                "estacion": self.estacion.id,
                "entradas": Decimal("200.00"),
                "salidas": Decimal("0.00"),
                "neto": Decimal("200.00"),
            },
            {
                "estacion": self.estacion2.id,
                "entradas": Decimal("500.00"),
                "salidas": Decimal("-100.00"),
                "neto": Decimal("600.00"),
            },
        ]

        self.assertEqual(resultado, esperado)

    def test_registro_y_filtado_de_datos_por_campo_cuenta(self):
        # Registros cuenta 1 ------------------
        self._mov(Tipo_movimiento.ENTRADA, "500")
        self._mov(Tipo_movimiento.SALIDA, "100")

        # Registros cuenta 2 ------------------
        self._mov(Tipo_movimiento.ENTRADA, "300", cuenta=self.cuenta2)
        self._mov(Tipo_movimiento.SALIDA, "-100", cuenta=self.cuenta2)

        with self.assertNumQueries(1):
                resultado = totales_por("cuenta")

        esperado = [
            {
                "cuenta": self.cuenta.id,
                "entradas": Decimal("500.00"),
                "salidas": Decimal("100.00"),
                "neto": Decimal("400.00"),
            },
            {
                "cuenta": self.cuenta2.id,
                "entradas": Decimal("300.00"),
                "salidas": Decimal("-100.00"),
                "neto": Decimal("400.00"),
            },
        ]

        self.assertEqual(resultado, esperado)

    def test_registro_y_filtado_de_datos_por_campo_y_fecha(self):
        # Registros fecha 1 ------------------
        self._mov(Tipo_movimiento.ENTRADA, "500", fecha = "2026-10-09")
        self._mov(Tipo_movimiento.SALIDA, "100", fecha = "2026-10-09")

        # Registros fecha 2 ------------------
        self._mov(Tipo_movimiento.ENTRADA, "300", fecha = "2026-10-10")
        self._mov(Tipo_movimiento.SALIDA, "-100", fecha = "2026-10-10")

        with self.assertNumQueries(1):
                resultado = totales_por("cuenta", hasta = "2026-10-09")

        esperado = [
            {
                "cuenta": self.cuenta.id,
                "entradas": Decimal("500.00"),
                "salidas": Decimal("100.00"),
                "neto": Decimal("400.00"),
            }
        ]

        self.assertEqual(resultado, esperado)

    def test_totales_por_campo_invalido(self):
        with self.assertRaises(ValueError):
            totales_por("otro")

    def test_saldo_de_caja_sin_saldo_inicial(self):
        with self.assertRaises(SaldoInicialNoConfigurado) as exc:
            saldo_de_caja()

        self.assertEqual(
            str(exc.exception),
            "No hay saldo inicial configurado."
        )

    def test_saldo_inicial_y_mov_registrado_exitoso(self):
        SaldoInicial.objects.create(
            monto = Decimal("2000.00"),
            fecha_referencia = "2026-10-1",
            creado_por = self.usuario
        )

        self._mov(Tipo_movimiento.ENTRADA, "200")

        self.assertEqual(
            Registro_Movimientos.objects.count(),
            1
        )