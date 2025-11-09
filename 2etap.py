import argparse
import sys
import os
import requests
import json
def get_direct_dependencies(package, repo, mode):
    if mode == 'real':
        url = f"{repo}/pypi/{package}/json"
        response = requests.get(url)
        if response.status_code != 200:
            raise ValueError(f"Ошибка получения данных для {package}: {response.status_code}")
        data = response.json()
        requires = data.get('info', {}).get('requires_dist', [])
        deps = []
        for req in requires:
            main_part = req.split(';')[0].strip()
            for sep in '<>=!~^ ([':
                if sep in main_part:
                    main_part = main_part.split(sep)[0]
            deps.append(main_part.strip())
        return deps
    elif mode == 'test':
        try:
            with open(repo, 'r') as f:
                lines = f.readlines()
            for line in lines:
                if line.startswith(package + ':'):
                    deps_str = line.split(':')[1].strip()
                    if deps_str:
                        deps = [d.strip() for d in deps_str.split(',')]
                    else:
                        deps = []
                    return deps
            return []
        except Exception as e:
            raise ValueError(f"Ошибка чтения файла {repo}: {e}")
    else:
        raise ValueError("Неверный режим")

def main():
    parser = argparse.ArgumentParser(description="1 этап: прототип для визуализации зависимостей пакетов")
    parser.add_argument('--package', type=str, required=True, help='Имя пакета')
    parser.add_argument('--repo', type=str, default='https://pypi.org', help='URL-адрес репозитория или путь к файлу тестового репозитория')
    parser.add_argument('--mode', type=str, default='real', choices=['real', 'test'], help='Режим работы: real (реальный репозиторий) или test (тестовый файл)')
    parser.add_argument('--output', type=str, default='graph.svg', help='Имя сгенерированного файла с изображением графа')
    parser.add_argument('--ascii', action='store_true', help='Режим вывода зависимостей в формате ASCII-дерева')
    parser.add_argument('--filter', type=str, default='', help='Подстрока для фильтрации пакетов (исключить пакеты, содержащие эту строку)')
    try:
        args = parser.parse_args()
        if args.mode == 'real':
            if not (args.repo.startswith('http://') or args.repo.startswith('https://')):
                raise ValueError("В реальном режиме repo должен быть URL (начинается с 'http://' или 'https://')")
        elif args.mode == 'test':
            if not os.path.exists(args.repo) or not os.path.isfile(args.repo):
                raise ValueError(f"В тестовом режиме repo должен быть существующим файлом: {args.repo} не найден или не файл") 
        print("Параметры:")
        print(f"package: {args.package}")
        print(f"repo: {args.repo}")
        print(f"mode: {args.mode}")
        print(f"output: {args.output}")
        print(f"ascii: {args.ascii}")
        print(f"filter: {args.filter}")
        deps = get_direct_dependencies(args.package, args.repo, args.mode)
        print("\nПрямые зависимости:")
        if not deps:
            print("→ У пакета нет прямых зависимостей.")
        else:
            for dep in deps:
                print(f"  {dep}")       
    except argparse.ArgumentError as e:
        print(f"Ошибка: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Ошибка валидации: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Неизвестная ошибка: {e}")
        sys.exit(1)
if __name__ == "__main__":
    main()