from nsimf.models.ExampleRunner import ExampleRunner

__author__ = "Mathijs Maijer"
__email__ = "m.f.maijer@gmail.com"

if __name__ == "__main__":
    # m = 'Craving vs Self control'
    # model = ExampleRunner(m)
    # output = model.simulate(100)
    # model.visualize(output)

    m = 'HIOM'
    model = ExampleRunner(m)
    output = model.simulate(15000)
    model.visualize(output)
