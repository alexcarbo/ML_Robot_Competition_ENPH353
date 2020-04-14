import os
import pickle


class savePlateCount:
    def __init__(self):
        self.plate_count = {}
        self.directory = "/home/fizzer/Desktop/353_ws/plates/"
        os.chdir(self.directory)

    def load_plates(self, filename):
        '''
        Load the number of plates saved to not overwrite older plates
        '''
        with open('{}.pickle'.format(filename)) as file:
            self.plate_count = pickle.load(file)
        file.close()
        print("Loaded file: {}".format(filename+".pickle"))

    def save_plates(self, filename):
        '''
        Save the nubmer of plates saved to not overwrite older plates
        '''
        if not os.path.isfile("{}.pickle".format(filename)):
            with open("{}.pickle".format(filename), 'wb') as file:
                self.plate_count["plate_count"] = 0
                pickle.dump(self.plate_count, file)
            file.close() 
            print("Created file {} with contents {} \n".format(filename+".pickle", self.plate_count))
        else:
            with open('{}.pickle'.format(filename), 'wb') as file:                
                pickle.dump(self.plate_count, file)
            file.close()
            print("Updated file {} with {} \n".format(filename+".pickle", self.plate_count))

    def update_plate_count(self, new_plate_count):
        self.plate_count["plate_count"] = new_plate_count

    def get_plate_count(self):
        return self.plate_count.get("plate_count", 0)