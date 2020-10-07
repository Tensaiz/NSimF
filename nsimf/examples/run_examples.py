from nsimf.models.ExampleRunner import ExampleRunner

__author__ = "Mathijs Maijer"
__email__ = "m.f.maijer@gmail.com"

if __name__ == "__main__":
    # m = 'Craving vs Self control'
    m = 'HIOM'

    model = ExampleRunner(m)
    output = model.simulate(500)
    model.visualize(output)
