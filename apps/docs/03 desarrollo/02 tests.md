# TESTS

El siguiente archivo, tiene como finalidad llevar un historial de las mutaciones que se le hacen al código para verificar que los test diseñado vigilan efectivamente lo planeado.

Es importante mencionar que este registro no se llevó a cabo desde el inicio del proyecto, por lo que varias mutaciones no tienen un registro. 

>[!NOTE]
>El registro de mutaciones se ha mantenido a través de decisiones que se han ido tomando durante el desarrollo, por lo que replicar cualquiera de estas pruebas, podría diferir un poco en cuanto al mensaje recibido. 

En caso de realizarlas en otro momento, agregar la evidencia a la siguiente tabla:

| id |    Archivo   |   Mutación   |     Falló    |   Mensaje  |
|----|--------------|--------------|--------------|------------|
|	1	|	validation.py	|	[0-9] → \d en NUMERO_CUENTA_PATRON	|	test_patron_ancho_completo	|	AssertionError: True is not false	|
|	2	|	models.py y 0012	|	quitar numero_cuenta_formato en ambos	|	test_base_rechaza_formato_invalido	|	AssertionError: IntegrityError not raised	|
|	3	|	models.py y 0012	|	quitar rubro_clave_no_vacia en ambos	|	test_base_rechaza_clave_vacia	|	AssertionError: IntegrityError not raised	|
|	4	|	models.py	|	quitar .exclude(pk=self.pk)	|	test_full_clean_no_falla_al_editar_el_mismo_rubro	|	raise ValidationError(errors) django.core.exceptions.ValidationError: {'rubro': ['Ya existe un rubro registrado con ese nombre']}	|
|	5	|	models.py	|	quitar el chequeo de duplicado en clean()	|	test_clean_detecta_duplicado_por_clave / test_full_clean_detecta_duplicado_distinto_pk	|	AssertionError: ValidationError not raisedv / AssertionError: 'Ya existe un rubro' not found in "{'__all__': ['El rubro no puede ser vacío']}"	|
|	6	|	import_cuentas.py	|	quitar el if not es_numero_cuenta_valido	|	test_numero_cuenta_invalido_en_csv  / test_numero_cuenta_invalido_tambien_falla_en_simulacion	|	AssertionError: 'Número de cuenta inválido' not found in "Fila 2: El rubro 'Nomina' no existe." / AssertionError: CommandError not raised	|
|	7	|	import_cuentas.py	|	recorrer filas_validadas[::-1] en handle	|	test_cada_cuenta_conserva_el_rubro_de_su_fila / test_cuenta_conserva_su_rubro_aun_si_se_reordena	|	AssertionError: <Rubro: Servicios> != <Rubro: Nómina>	|
|	8	|	roles.py	|	agregar view_registro_movimientos a Soporte en roles.py	|	test_soporte_sin_permisos_de_movs	|	AssertionError: Items in the first set but not the second: 'view_registro_movimientos'	|
|	9	|	roles.py	|	agregar change_registro_movimientos a un rol	|	test_no_delete_en_registro_movs /  test_user_tipo_permisos	|	AssertionError: True is not false	|
|	10	|	roles.py	|	quitar view_registro_movimientos a un rol de captura	|	test_permisos_users_captura	|	AssertionError: False is not true	|
|	11	|	admin.py	|	registrar Registro_Movimientos en admin.py	|	test_movimientos_no_estan_en_el_admin	|	AssertionError: <class 'apps.movs.models.Registro_Movimientos'> unexpectedly found in {<class 'django.contrib.auth.models.Group'>…	|
|	12	|	roles.py	|	quitar add_registro_movimientos a Capturista	|	Fallaron 18 pruebas	|	AssertionError	|
|	13	|	roles.py	|	quitar view_registro_movimientos a Auditor	|	test_permisos_exactos_por_rol	|	AssertionError: Items in the second set but not the first: 'view_registro_movimientos'	|
|	14	|	roles.py	|	agregar add_registro_movimientos a Auditor	|	test_user_con_grupo_sin_permisos_captura / test_permisos_exactos_por_rol	|	AssertionError: 200 != 403 / AssertionError: Items in the first set but not the second: 'add_registro_movimientos'	|
|	15	|	roles.py	|	cambiar movs.add_registro_movimientos por catalogos.add_cuenta en Capturista	|	Fallaron 18 pruebas	|	.	|
|	16	|	roles.py	|	renombrar Auditor a Visualizador en roles.py	|	FAILED (failures=1, errors=4)	|	.	|
|	17	|	inmutable.py	|	quitar el if not self._state.adding de save()	|	test_permiso_denegado_cambio_de_monto	|	django.db.utils.IntegrityError: duplicate key value violates unique constraint	|
|	18	|	inmutable.py	|	quitar el delete() del modelo	|	test_permiso_denegado_delete_mov	|	AssertionError: PermissionDenied not raised	|
|	19	|	inmutable.py	|	quitar el update() del queryset	|	test_permiso_denegado_update_monto	|	AssertionError: PermissionDenied not raised	|
|	20	|	inmutable.py	|	quitar el delete() del queryset	|	test_permiso_denegado_delete_all_movs	|	AssertionError: PermissionDenied not raised	|
|	21	|	models.py / saldoinicial /migracion 003	|	quitar unique=True de unico	|	test_base_rechaza_segunda_fila / test_segunda_fila_con_bulk_create_lanza_integrity_error	|	AssertionError: IntegrityError not raised	|
|	22	|	models.py / saldoinicial /migracion 004	|	quitar el CheckConstraint de unico	|	test_base_rechaza_unico_falso / test_unico_false_lanza_integrity_error	|	AssertionError: IntegrityError not raised	|
|	23	|	config_si.py	|	quitar la comparación de montos de confirmación	|	test_aplicar_confirmacion_saldo_diferente	|	AssertionError: CommandError not raised	|
|	24	|	config_si.py	|	quitar el rechazo por saldo existente	|	test_saldo_existente_no_se_guarda	|	django.db.utils.IntegrityError: duplicate key value violates unique constraint 	|
|	25	|	config_si.py	|	invertir if not aplicar	|	test_simulacion_no_escribe	|	django.core.management.base.CommandError	|
|	26	|	config_si.py	|	fullmatch por match en el parser	|	test_aplicar_confirmacion_monto_no_valido / test_monto_si_invalido	|	AssertionError	|
|	27	|	models.py / saldoinicial /migracion 003	|	quitar el CheckConstraint de monto >= 0	|	test_base_rechaza_monto_negativo	|	AssertionError: IntegrityError not raised	|
|	28	|	saldos.py / saldo_de_movimientos	|	en saldo_de_movimientos, entradas + salidas	|	test_crear_movimientos_con_bulk_create / test_saldo_de_caja_con_los_cuatro_movimientos / test_saldo_de_caja_filtrado_fecha / test_salida_negativa_suma / test_salida_positiva_resta	|	Todas reciben un resultado similar a AssertionError: Decimal('3750.00') != Decimal('1250.00')	|
|	29	|	saldos.py / saldo_de_movimientos	|	salidas - entradas	|	test_crear_movimientos_con_bulk_create / test_entrada_negativa_resta / test_entrada_positiva_suma / test_saldo_de_caja_con_los_cuatro_movimientos / test_saldo_de_caja_filtrado_fecha / test_salida_negativa_suma / test_salida_positiva_resta /test_tres_movimientos_de_diez_centavos_suman_treinta	|	Todas reciben un resultado similar a AssertionError: AssertionError: Decimal('-200.00') != Decimal('200.00')	|
|	30	|	saldos.py / saldo_de_movimientos	|	Value(CERO) por Value(Decimal("1.00")) en Coalesce	|	test_entrada_negativa_resta / test_entrada_positiva_suma / test_registro_y_filtado_de_datos_por_campo_cuenta / test_registro_y_filtado_de_datos_por_campo_estacion / test_saldo_de_caja_filtrado_fecha / test_salida_negativa_suma / test_salida_positiva_resta / test_tres_movimientos_de_diez_centavos_suman_treinta 	|	Errores similares a AssertionError: Decimal('51.00') != Decimal('50.00')	|
|	31	|	saldos.py	|	quitar el filtro hasta	|	test_saldo_de_caja_filtrado_fecha	|	AssertionError: Decimal('50.00') != Decimal('100.00')	|
|	32	|	saldos.py	|	fecha_caja__lte por __lt	|	test_saldo_de_caja_filtrado_fecha	|	AssertionError: Decimal('200.00') != Decimal('100.00')	|
|	33	|	saldos.py	|	saldo_de_caja ignora el saldo inicial	|	test_saldo_de_caja_con_los_cuatro_movimientos / test_crear_movimientos_con_bulk_create	|	Errores similares a AssertionError: Decimal('-80.00') != Decimal('920.00')	|
|	34	|	saldos.py	|	si no hay saldo inicial, devolver CERO en vez de lanzar	|	test_saldo_de_caja_sin_saldo_inicial	|	AssertionError: SaldoInicialNoConfigurado not raised	|
|	35	|	saldos.py	|	filtrar los movimientos por fecha_caja >= fecha_referencia	|	test_saldo_de_caja_filtrado_fecha	|	AssertionError: Decimal('-150.00') != Decimal('100.00')	|
|	36	|	saldos.py	|	en totales_por, neto = entradas + salidas	|	test_registro_y_filtado_de_datos_por_campo_cuenta / test_registro_y_filtado_de_datos_por_campo_estacion / test_registro_y_filtado_de_datos_por_campo_y_fecha	|	Todas las pruebas tuvieron un error similar a este: AssertionError: Lists differ: [{'cu[36 chars]00'), 'salidas': Decimal('100.00'), 'neto': Decimal('600.00')}] != [{'cu[36 chars]00'), 'salidas': Decimal('100.00'), 'neto': Decimal('400.00')}]	|
|	37	|	saldos.py	|	_suma_tipo: Value(Decimal("1.00") if tipo == Tipo_movimiento.ENTRADA else CERO) en el Coalesce, no en el Case.	|	test_sin_movimientos_devuelve_cero_decimal	|	AssertionError: Decimal('1.00') != Decimal('0.00')	|
|	38	|	saldos.py	|	dos agregados en vez de uno (en saldo_de_movimientos)	|	test_crear_movimientos_con_bulk_create	|	AssertionError: 2 != 1 : 2 queries executed, 1 expected	|
|	39	|	saldos.py	|	N+1 (una consulta por fila)	|	test_crear_movimientos_con_bulk_create	|	AssertionError: 51 != 1 : 51 queries executed, 1 expected	|
|	40	|	saldos.py	|	saldo_de_caja: return inicial - saldo_de_movimientos(...)	|	test_crear_movimientos_con_bulk_create / test_saldo_de_caja_con_los_cuatro_movimientos	|	Errores similares a AssertionError: Decimal('-250.00') != Decimal('2250')	|
|	41	|	saldos.py	|	totales_por: quitar el if hasta is not None: qs = qs.filter(...)	|	test_registro_y_filtado_de_datos_por_campo_y_fecha	|	AssertionError: Lists differ: [{'cu[27 chars]mal('800.00'), 'salidas': Decimal('0.00'), 'ne[19 chars]0')}] != [{'cu[27 chars]mal('500.00'), 'salidas': Decimal('100.00'), '[21 chars]0')}]	|
|	42	|	saldos.py	|	totales_por: fecha_caja__lte → fecha_caja__lt	|	test_registro_y_filtado_de_datos_por_campo_y_fecha	|	AssertionError: Lists differ: [] != [{'cuenta': 31, 'entradas': Decimal('500.0[57 chars]0')}]	|
|	43	|	saldos.py	|	totales_por: quitar el if campo not in ("cuenta", "estacion"): raise ValueError	|	test_totales_por_campo_invalido / test_totales_por_campo_valido_no_permitido	|	django.core.exceptions.FieldError: Cannot resolve keyword 'otro' into field. Choices are: creado_en, creado_por, creado_por_id, cuenta, cuenta_id, descripcion, estacion, estacion_id, fecha_caja, id, monto, tipo_movimiento  / AssertionError: ValueError not raised	|
|	44	|	roles.py	|	Quitar ver_saldos de Capturista en roles.py	|	test_permisos_exactos_por_rol	|	AssertionError: Items in the second set but not the first: 'view_saldos'	|
|	45	|	roles.py	|	Quitar ver_saldos de Auditor	|	test_permisos_exactos_por_rol	|	AssertionError: Items in the second set but not the first: 'view_saldos'	|
|	46	|	roles.py	|	Añadir ver_saldos a Soporte	|	test_soporte_sin_permisos_de_movs / test_permisos_exactos_por_rol	|	AssertionError: Items in the first set but not the second: 'view_saldos'	|
|	47	|	models.py (movs) / migracion 005	|	Cambiar el codename del permiso en el modelo y en la migración 0005 a la vez (regla: modelo y migración juntos)	|	.	|	.	|