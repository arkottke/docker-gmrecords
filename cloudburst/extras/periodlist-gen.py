#!/usr/bin/python3
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-dams', dest='dams', required=True, help='An individual, list or range of dams, e.g. "01"')
parser.add_argument('-periods', dest='periods', required=True, help='An individual, list or range of periods, e.g. "01"')

# convert an input string e.g. comma separated list or a range to a padded list
def convertInputToList(inputString:str, padding:int):
    items = []
    bIsRange = '-' in inputString
    if bIsRange:
        items = inputString.split('-')
    else:
        items = inputString.split(',')
    
    outputItems = []

    # convert the range to a list, assumes that the numbers are continuous
    if bIsRange:
        # if it's a range, assume first and last are in order and we fetch each site in between
        iFirst = int(items[0])
        iLast = int(items[1])

        # build a list of sites
        for i in range(iFirst, iLast+1):
            item = str(i).zfill(padding)
            outputItems.append(item)
    else:
        # format the numbers in the list with the correct padding
        for i in items:
            item = str(i).zfill(padding)
            outputItems.append(item)
    return outputItems

# starts batch jobs in AWS, running the dams/periods specified
def main(args):
    if args.dams != '' and args.periods != '':
        sites = convertInputToList(args.dams,3)
        periods = convertInputToList(args.periods,2)
        for site in sites:
            for period in periods:
                print(f'Dam{site}/Period{period}')

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
