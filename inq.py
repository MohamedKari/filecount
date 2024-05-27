import inquirer
questions = [
  inquirer.List('size',
                message="What size do you need?",
                choices=['Jumbo', 'Large', 'Standard', 'Medium', 'Small', 'Micro'],
                default="Standard",
                carousel=True,
                other=True,
            ),
]
answers = inquirer.prompt(questions)
