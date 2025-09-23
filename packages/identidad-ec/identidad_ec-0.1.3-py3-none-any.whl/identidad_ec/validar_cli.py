import argparse
from identidad_ec.utils import validar_identificacion
from identidad_ec.ruc import validar_ruc

def main():
    parser = argparse.ArgumentParser(description="Validar cédulas y RUCs ecuatorianos")
    parser.add_argument("numero", nargs="?", help="Número de cédula o RUC")
    parser.add_argument("--estricto", action="store_true", help="Aplicar validación estricta (módulo 11 para RUC)")
    parser.add_argument("--generar", choices=["juridico", "publico"], help="Generar RUC válido ficticio para pruebas")
    
    args = parser.parse_args()

    if args.generar:
        if args.generar == "juridico":
            ruc = validar_ruc()
            print(f"RUC Jurídico válido: {ruc}")
        elif args.generar == "publico":
            ruc = validar_ruc()
            print(f"RUC Público válido: {ruc}")
        return

    if not args.numero:
        print("Debe ingresar un número de cédula o RUC para validar.")
        return

    resultado = validar_identificacion(args.numero, estricto=args.estricto)
    print(f"Resultado: {resultado}")

if __name__ == "__main__":
    main()
