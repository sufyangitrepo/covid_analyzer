import math
import pandas as pd
from pandas import errors
import enum
from enum import Enum

"""
    This project is related to analyze covid status 
    with three common functionalities 
    1. calculate the ratio of recovered cases in any given country => recovered_ratio()
    2. calculate the average death rate on any given measure      =>  averager_death_rate()
    3. find 5 mostly adopted efficient measures                  =>   efficient_measures()
    
"""


class CovidAnalyzer:

    def __init__(self, covid_file_path: str, measure_file_path: str):

        """ Constructor takes two parameters one is covid file path
                another is , covid measures file path
            """
        self.__covid_stats = None
        self.__safety_measures_states = None
        self.read_measures_stats(safety_measures_file_path=measure_file_path)
        self.read_covid_stats(covid_file_path=covid_file_path)

    def read_measures_stats(self, safety_measures_file_path: str):

        """
                this function will be used to read the covid measures stats
                having  one paramter that is the path of file
            """

        try:
            self.__safety_measures_states = pd.read_csv(safety_measures_file_path)
        except FileNotFoundError:
            raise FileNotFoundError(
                'There is no file with this \'{}\''.format(safety_measures_file_path))
        except errors.EmptyDataError:
            raise errors.EmptyDataError('There is no data')
        except Exception:
            raise Exception('Some other exception')

    def read_covid_stats(self, covid_file_path: str):

        """ This function also used to read the file that has covid stats
                take one argument as file location/path
            """
        try:
            self.__covid_stats = pd.read_csv(covid_file_path)
        except FileNotFoundError:
            raise FileNotFoundError('There is no file with this name \'{}\''.format(covid_file_path))
        except errors.EmptyDataError:
            raise errors.EmptyDataError('there is no data in this file')
        except Exception:
            raise Exception('some error you cant proceed')

    def get_covid_stats(self):
        return self.__covid_stats

    def get_measure_stats(self):
        return self.__safety_measures_states

    def recovered_ratio(self, country_name: str):

        """ This function calculates the ratio of recovered cases over total cases
                takes one argument as astring country name
            """

        try:
            rec = self.fetch_records('country', country_name, FileStatus.COVID_STATS_FLAG)
            series_of_recovered_cases = rec['total_recovered']
            series_of_total_cases = rec['total_cases']
        except errors.EmptyDataError:
            raise errors.EmptyDataError('there is no data')
        except errors.DtypeWarning:
            raise errors.DtypeWarning('Data type mismatch error')
        except Exception:
            raise Exception('some other errors')
        if len(series_of_recovered_cases) > 0 and len(series_of_total_cases) > 0:
            recovered = series_of_recovered_cases.iloc[0]
            total_case = series_of_total_cases.iloc[0]
            print(
                'Ratio of  Recovered_cases/total_cases in {} = {:.2}'.format(country_name, recovered / total_case))
        else:
            print('There is no country with this name!!')

    def fetch_records(self, col_name, search, flag):

        """This function will return the record from covid stats file corresponding given country name.
               it takes the three parameters :
               column name => from which have to search
               search => use to filter the data
               flag   => from which file have to fetch the data .
               it may be   COVID_STATS_FLAG or MEASURES_STATS_FLAG
            """

        if flag == FileStatus.COVID_STATS_FLAG:
            return self.get_covid_stats().loc[self.get_covid_stats()[col_name] == search]

        elif flag == FileStatus.MEASURES_STATS_FLAG:
            return self.get_measure_stats().loc[self.get_measure_stats()[col_name] == search]
        else:
            return 'invalid flag'

    def average_death_rate(self, measure: str):
        """ This function calculates the average death rate from all over the
                glob depending on the measure the is given to it as input
            """
        total_deaths_rate = 0

        try:
            series_of_countries_with_measures = \
                self.fetch_records('measure', measure, FileStatus.MEASURES_STATS_FLAG)['country']

            for i in series_of_countries_with_measures:
                total_deaths_series = self.fetch_records('country', i, FileStatus.COVID_STATS_FLAG)['total_deaths']
                total_cases_series = self.fetch_records('country', i, FileStatus.COVID_STATS_FLAG)['total_cases']
                if len(total_cases_series) > 0 and len(total_deaths_series) > 0:
                    deaths_per_measure = total_deaths_series.iloc[0]
                    cases_per_measure = total_cases_series.iloc[0]
                    if not math.isnan(deaths_per_measure) and not math.isnan(cases_per_measure):
                        death_rate = cases_per_measure / deaths_per_measure
                        total_deaths_rate += death_rate

            if len(series_of_countries_with_measures) > 0:
                print('Average Death Rate: {:.6}'. \
                      format(total_deaths_rate / len(series_of_countries_with_measures)))
            else:
                print('there is no country with this measure')
        except Exception as exception:
            print(exception)

    def efficient_measures(self, ):

        """ This function gives the five mostly adopted measures with their
                efficiency . first it selects five measures that is mostly adopted
                then acording to this measures search all countries which adopt this measure
                and in this way it calculate the efficiency of each measure
            """

        try:
            # value_counts() function will count the occurrence of each measure .
            # i just get first five that is mostly adopted
            mostly_adopted_measure = self.get_measure_stats().loc[
                self.get_measure_stats()['measure'].value_counts()[0:5]]

            # Convert  them into list
            list_of_mostly_adopted_measures = list(mostly_adopted_measure['measure'])

            # Dictionary for result
            dict_of_result = {}
        except errors.EmptyDataError as exception:
            return errors.EmptyDataError('empty data error')
            # Iterate the mostly adopted measure list and fetch each measures efficiency accordingly
        for index in range(len(list_of_mostly_adopted_measures)):
            sum_of_recovered_cases = 0
            sum_of_total_cases = 0
            series_of_countries = self.fetch_records('measure',
                                                     list_of_mostly_adopted_measures[index],
                                                     FileStatus.MEASURES_STATS_FLAG)['country']
            for country in series_of_countries:
                data_frame = self.fetch_records('country', country, FileStatus.COVID_STATS_FLAG)
                recovered_cases = data_frame['total_recovered']
                total_cases = data_frame['total_cases']
                if len(recovered_cases) > 0 and len(total_cases) > 0 and not math.isnan(
                        recovered_cases.iloc[0]) and not math.isnan(total_cases.iloc[0]):
                    sum_of_total_cases += total_cases.iloc[0]
                    sum_of_recovered_cases += recovered_cases.iloc[0]

            dict_of_result[list_of_mostly_adopted_measures[index]] = \
                sum_of_recovered_cases / sum_of_total_cases
        return dict_of_result  # return final result

"""
   Enum that has two flags one for covid stats
    and other for measure stats
"""


class FileStatus(Enum):
    COVID_STATS_FLAG = 0
    MEASURES_STATS_FLAG = 1


if __name__ == "__main__":
    try:
        covidAnalyzer = CovidAnalyzer(covid_file_path='covid_cases_stats.csv',
                                      measure_file_path='covid_safety_measures.csv')
        covidAnalyzer.recovered_ratio(input('enter country name: '))
        covidAnalyzer.average_death_rate(input('enter measure: '))
        print(covidAnalyzer.efficient_measures())
    except Exception as ex:
        print(ex)
