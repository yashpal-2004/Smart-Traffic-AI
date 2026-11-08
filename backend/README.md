# Backend simulator

Run the current deterministic simulator checks from this directory:

```sh
python -m unittest discover -s tests -v
```

The simulator is a simplified educational model: one vehicle per active approach may clear per second, and north/south and east/west are the only signal phases.
