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
4. The leader and validator independently classify each component using the stored guide text. The output is accepted only when the validators agree on the category. Non-UNKNOWN decisions must include a quote found in the stored guide.
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

## Consensus and data integrity

The policy text is included in the contract state and cannot be changed for an existing profile. Its hash binds each evaluation to that exact text. Validators independently classify the submitted components against the same stored snapshot. The contract validates the output schema, restricts categories to a fixed set, and checks that each non-UNKNOWN leader quote occurs in the stored policy text.

## Limitations

- The profile registrant supplies both the source URL and the policy text. The contract records this provenance but does not authenticate that the URL belongs to an official authority or independently fetch the page.
- A consensus result is an interpretation of the registered snapshot, not an official or legal waste-disposal certification.
- The model may return UNKNOWN when the guide is ambiguous or does not clearly cover an item.
- CivicSort does not handle images, payments, or physical collection.

## Evidence

### GitHub

- Repository: https://github.com/0xmojol/civicsort-genlayer
- Contract source: https://github.com/0xmojol/civicsort-genlayer/blob/main/contracts/civic_sort.py

### GenLayer Explorer

- Contract: https://explorer-studio.genlayer.com/address/0x838Cfb5F6fb88fdF2317Cef1FED420Dae873e03c
- Deployment transaction: https://explorer-studio.genlayer.com/tx/0xd55176d536ecedcce8480ad0676aeae4c4a5f526b18e4a33accaa5571db72eb7
- Profile registration transaction: https://explorer-studio.genlayer.com/tx/0xe03ebd599ffafa91b15d431f6f5ff0b77f24610dd7637306b3fcd76ef7f97df2
- Consensus evaluation transaction: https://explorer-studio.genlayer.com/tx/0xfd6e647e22b6596cb926596e8eb7ec21f201f196b8fae0f6fa9932df406385d9

The live evaluation returned RECYCLING for Verbundstoff (Getränkekarton), with local stream Gelbe Tonne and a quote from the registered policy snapshot. The stored evaluation was then retrieved through the read-only get_evaluation("0") method in Studio.

The listed transactions show FINALIZED, Accepted, and 0 GEN value in the Explorer. Transaction value does not establish the cost of all future network interactions.
