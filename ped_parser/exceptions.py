class WrongAffectionStatus(Exception):
    """Error for wrong affection status"""
    def __init__(self, cmms_id, valid_statuses, message = ""):
        """
        Arguments:
            cmms_id (str): A string that describes the id
            valid_statuses (list): A list with the valid affections statuses
        """
        super(WrongAffectionStatus, self).__init__()
        self.cmms_id = cmms_id
        self.valid_statuses = valid_statuses
        self.message = message
    
    def __str__(self):
        return self.message

class WrongPhenotype(Exception):
    """Error for wrong phenotype"""
    def __init__(self, cmms_id, phenotype, affection_status, message=""):
        """
        Arguments:
            cmms_id (str): A string that describes the id
            phenotype (int): A int with the ped affections status
            affection_status (str): A str that describes the cmms 
                                    affections status
        """
        super(WrongPhenotype, self).__init__()
        self.cmms_id = cmms_id
        self.phenotype = phenotype
        self.affection_status = affection_status
        self.message = message

    def __str__(self):
        return self.message

class WrongGender(Exception):
    """Error for wrong gender"""
    def __init__(self, cmms_id, sex, sex_code, message=""):
        """
        Arguments:
            cmms_id (str): A string that describes the id
            sex (int): A int with the ped sex code
            sex_code (str): A str that describes the cmms 
                                    sex
        """
        super(WrongGender, self).__init__()
        self.cmms_id = cmms_id
        self.sex = sex
        self.sex_code = sex_code
        self.message = message

    def __str__(self):
        return self.message

class PedigreeError(Exception):
    """Error inconcistenies in ped file"""
    def __init__(self, family_id, individual_id, message=""):
        """
        Arguments:
            family_id (str): A string that describes the family id
            individual_id (str): A str with the individual id
        """
        super(PedigreeError, self).__init__()
        self.family_id = family_id
        self.individual_id = individual_id
        self.message = message

    def __str__(self):
        return self.message

