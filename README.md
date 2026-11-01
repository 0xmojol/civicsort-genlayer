# CivicSort

**CivicSort is a general-purpose GenLayer Intelligent Contract for interpreting local packaging-sorting guides.** A user registers an immutable policy profile for any region, including the guide text and its source URL. Other users can submit a packaging item and its components for validator-consensus classification.

CivicSort does not hard-code one city or assume that sorting rules are universal. Each result is tied to the exact policy profile and its SHA3-256 hash.

## Problem

Packaging can contain several materials, and collection rules differ between regions. A printed policy may say how a beverage carton, paper wrapper, or metal lid should be handled, but translating those instructions into a consistent result can require interpretation.

CivicSort gives that interpretation a shared, auditable on-chain record rather than returning an unrecorded answer from a single model.

## Workflow

1. A caller registers a profile with a unique ID, region label, HTTPS source URL, and a text snapshot of the sorting guide.
2. The contract stores the profile and the SHA3-256 hash of the exact guide text. A profile ID cannot be overwritten; a revised guide needs a new profile ID.
3. A caller submits an item description and one to five packaging components against a profile.
4. The leader and validator independently classify each component using the stored guide text. The validator checks agreement on the category and local collection stream. A non-UNKNOWN decision must include a supporting quote found in the stored guide.
5. The contract stores the result with the profile ID, policy hash, source URL, item, components, categories, local stream labels, and supporting quotes.

## Categories

- RECYCLING
- ORGANIC
- RESIDUAL
- SPECIAL
- UNKNOWN

If the guide is silent or ambiguous, or a supporting quote cannot be found in the frozen text, the safe result is UNKNOWN.

## Contract interface

### Write methods

- register_profile(profile_id, region_label, source_url, policy_text)
  - Registers an immutable, user-supplied guide snapshot.
- evaluate_item(profile_id, item_description, components_json)
  - Runs validator consensus and stores a classification record.

### Read methods

- get_profile(profile_id)
- get_evaluation(evaluation_id)
- get_counts()

## Development checks

The Python development dependencies are pinned in requirements.txt. Use Python 3.12 or newer.

### Install dependencies

    python -m venv .venv
    source .venv/bin/activate
    python -m pip install -r requirements.txt

The commands below use a macOS/Linux shell or Git Bash.

### Direct Mode tests

Run the mocked Direct Mode tests:

    python -m pytest tests/direct/ -v

The pinned Direct Mode runner currently requests an archive name that is not published by the corresponding GenVM release. If pytest fails before collecting or executing tests with an HTTP 404 while downloading genvm-universal.tar.xz, pre-populate its cache with the published runner archive:

    mkdir -p ~/.cache/gltest-direct
    curl -fL https://github.com/genlayerlabs/genvm/releases/download/v0.3.0-rc7/genvm-runners-all.tar.xz -o ~/.cache/gltest-direct/genvm-universal-v0.3.0-rc7.tar.xz

Then run the Direct Mode test command again.

### GenVM lint and validation

    GENVM_VERSION=v0.3.0-rc7 genvm-lint check contracts/civic_sort.py

Validation performed for the current contract source:

- Direct Mode tests: 4 passed.
- GenVM lint and validation: passed.
- Python syntax compilation: passed.

## Consensus and data integrity

The policy text is included in the contract state and cannot be changed for an existing profile. Its hash binds each evaluation to that exact text. The leader and validator independently classify the submitted components against the same stored snapshot. The contract validates the output schema, restricts categories to a fixed set, compares the category and normalized local stream, and checks that non-UNKNOWN supporting quotes occur in the stored policy text.

## Limitations

- The profile registrant supplies both the source URL and the policy text. The contract records this provenance but does not authenticate that the URL belongs to an official authority or independently fetch the page.
- A consensus result is an interpretation of the registered snapshot, not an official or legal waste-disposal certification.
- The model may return UNKNOWN when the guide is ambiguous or does not clearly cover an item.
- CivicSort does not handle images, payments, or physical collection.

## Evidence

### GitHub

- Repository: https://github.com/0xmojol/civicsort-genlayer
- Contract source: https://github.com/0xmojol/civicsort-genlayer/blob/main/contracts/civic_sort.py
- Direct Mode tests: https://github.com/0xmojol/civicsort-genlayer/tree/main/tests/direct
- Python dependencies: https://github.com/0xmojol/civicsort-genlayer/blob/main/requirements.txt

### GenLayer Explorer

- Current contract: https://explorer-studio.genlayer.com/address/0xa97F6764912bC738af425516A39dCdd4E8a61314
- Deployment transaction: https://explorer-studio.genlayer.com/tx/0xcd96ab693e4158876646172f3dbb36570747380fc0a9e7ba7f78a7f2540cc113
- Profile registration transaction: https://explorer-studio.genlayer.com/tx/0xedfc8e3d03151bf3f0e71f917ebc8c809e4b8c71e65103a47035c1c13762ec5f
- Consensus evaluation transaction: https://explorer-studio.genlayer.com/tx/0xf0c7eadc5ded17d700df4e93d74e86b4b4bc16ccc571ebeb5520086d1e735436

The current evaluation returned RECYCLING for Verbundstoff (Getränkekarton), with local stream Gelbe Tonne and a supporting quote from the registered policy snapshot. The read-only get_evaluation("0") method returned the stored record, and get_counts returned one profile and one evaluation.

The previous contract instance remains at 0x838Cfb5F6fb88fdF2317Cef1FED420Dae873e03c. The current source and latest evaluation evidence above refer to the new instance.

### Other

- GenLayer Test documentation: https://docs.genlayer.com/api-references/genlayer-test
- GenLayer Testing Suite: https://github.com/genlayerlabs/genlayer-testing-suite
- GenLayer upgradability documentation: https://docs.genlayer.com/developers/intelligent-contracts/features/upgradability
