# kitchen-scripts

Small command-line tools for cooks. Plain Python 3, no dependencies: download a script and run it.

| Script | What it does |
|---|---|
| [`scale_recipe.py`](scale_recipe.py) | Scales every ingredient in a recipe: double it, halve it, or go from 4 servings to 6. |
| [`cup2g.py`](cup2g.py) | Converts cups, tablespoons and teaspoons to grams for common baking ingredients. |

Both understand the way recipes are really written: `2`, `1.5`, `1/2`, `1 1/2`, `½`, `1½`, `a pinch`, and ranges like `2-3` or `2 to 3`. Lines they don't understand (steps, headings, "salt to taste") are left exactly as they are.

## Install

You need Python 3.8 or newer. Nothing else.

```bash
git clone https://github.com/mouadbenrahou/kitchen-scripts.git
cd kitchen-scripts
```

## scale_recipe.py

```bash
python3 scale_recipe.py --to 6 examples/pancakes.txt        # uses the "Serves 4" line in the recipe
python3 scale_recipe.py --from 4 --to 6 examples/pancakes.txt
python3 scale_recipe.py --factor 2 examples/pancakes.txt     # also 0.5, 1.5 or 3/2
cat examples/pancakes.txt | python3 scale_recipe.py --factor 1/2
```

```text
Serves 4                        Serves 6
2 cups all-purpose flour   →    3 cups all-purpose flour
½ tsp salt                      3/4 tsp salt
2-3 cloves garlic               3 to 4 1/2 cloves garlic
a pinch of nutmeg               1 1/2 pinches nutmeg
```

Amounts are rounded to the nearest eighth, units are pluralised (`1 cup` → `2 cups`), and with `--to` the servings line is updated too.

## cup2g.py

```bash
python3 cup2g.py 1 cup flour            # 125 g flour
python3 cup2g.py examples/pancakes.txt  # converts a whole recipe
python3 cup2g.py --help                 # lists every known ingredient
```

```text
2 cups all-purpose flour   →    250 g all-purpose flour
½ cup butter                    113.5 g butter
2 tbsp sugar                    25 g sugar
1 to 2 cups oats                90 to 180 g oats
3 eggs                          3 eggs
```

It knows about 30 common ingredients (flours, sugars, butter, milk, oils, oats, cocoa...). The gram values per cup are in the `GRAMS_PER_CUP` table at the top of the script: add your own in one line.

## Tests

```bash
python3 -m unittest discover -s tests -t .
```

## History

I wrote these in 2022 for my own cooking and kept using them. In 2026 I cleaned them up for open source: shared parsing in `quantities.py`, range support in `cup2g.py`, UTF-8 file handling, proper `--help`, and tests.

## License

[MIT](LICENSE) © Mouad Benrahou
