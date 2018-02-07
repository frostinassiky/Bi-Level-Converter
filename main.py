from COCOMissing import COCOMissingGenerator
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        mr = float(sys.argv[1])
    else:
        mr = 0.8
    print ('Missing Rate ', mr)
    g = COCOMissingGenerator(mr)

    g.drop_freq()