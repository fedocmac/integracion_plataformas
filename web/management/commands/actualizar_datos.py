from django.core.management.base import BaseCommand
import json, requests
from pathlib import Path
from django.conf import settings

class Command(BaseCommand):
    help = 'Actualiza products.json, inventory.json y category.json desde la API externa'

    def handle(self, *args, **kwargs):
        try:
            base_dir = Path(settings.BASE_DIR) / 'datos'
            base_dir.mkdir(parents=True, exist_ok=True)

            urls = {
                "products": "https://integracionstock-etefhkhbcadegaej.brazilsouth-01.azurewebsites.net/products",
                "inventory": "https://integracionstock-etefhkhbcadegaej.brazilsouth-01.azurewebsites.net/inventory",
                "category": "https://integracionstock-etefhkhbcadegaej.brazilsouth-01.azurewebsites.net/product-category"
            }

            for nombre, url in urls.items():
                response = requests.get(url)
                response.raise_for_status()

                datos = response.json()

                if datos:  # Solo si hay datos para guardar
                    with open(base_dir / f"{nombre}.json", "w", encoding="utf-8") as f:
                        json.dump(datos, f, ensure_ascii=False, indent=4)
                    self.stdout.write(f"Archivo {nombre}.json actualizado.")
                else:
                    self.stdout.write(f"Archivo {nombre}.json NO actualizado porque no hay datos nuevos.")

            self.stdout.write(self.style.SUCCESS('✔ Archivos actualizados correctamente (cuando hubo datos).'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✘ Error: {e}'))