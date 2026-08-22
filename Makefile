.PHONY: verify qbank-dry supernova-dry help

help:
	@echo "UC Lab Free University — maintainer targets"
	@echo "  make verify         verify the flagship offline campus"
	@echo "  make qbank-dry      dry-run the practice-bank generator"
	@echo "  make supernova-dry  dry-run every supernova pack"

verify:
	python3 tools/verify_campus.py

qbank-dry:
	python3 uc_qbank_gen.py --dry-run

supernova-dry:
	python3 uc_supernova_gen.py vendor --dry-run
	python3 uc_supernova_gen.py migration --dry-run
	python3 uc_supernova_gen.py sev --dry-run
	python3 uc_supernova_gen.py mastery --dry-run
