def choose_image_strategy(source_url=None):

    print("\nSkipping official image extraction...")
    print("Using AI-generated visual strategy.")

    return {
        "strategy": "GENERATED_VISUAL",
        "image": None
    }


if __name__ == "__main__":

    result = choose_image_strategy()

    print("\nFINAL STRATEGY:")
    print(result)