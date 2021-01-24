import logging

class FieldLabels:
    def __init__(self,labels=None):
        self.labels = {l:[] for l in labels}
        self.autofill = True
        self.last_label = None
        
    def add_labels(self,labels):
        new_add = False
        if isinstance(labels,str):
            labels = [labels]
        for l in labels:
            if l not in self.labels:
                self.labels[l] = []
                new_add = True
        return new_add

    def add_example(self,label,annotation):
        if label not in self.labels:
            self.add_labels([label])

        (text,first,last) = annotation
        first = int(first.split('.')[1])
        last  = int(last.split('.')[1])

        # need this to remove extra spaces at the end
        while text[-1] == ' ':
            last -= 1
            text = text[:-1]
            logging.debug("removing spaces {} {} {}".format(first,last,text))

        self.labels[label] += [(first,last,text)]
        self.last_label = label
        return ("1.{}".format(first),"1.{}".format(last))
    
    def get_line(self):
        ret_array = []
        for l in self.labels:
            for ids in self.labels[l]:
                ret_array += [(ids[0],ids[1],l)]
        return ret_array

    def all_text(self):
        outstring = ''
        for l in self.labels:
            for tag in self.labels[l]:
                outstring += '{} : {}\n'.format(l, tag)
        return outstring

    def reset_labels(self):
        self.labels = {l:[] for l in self.labels}

    def remove_last(self):
        labels = None
        if self.last_label is not None:
            labels = [self.last_label] + list(self.labels[self.last_label].pop())
        self.last_label = None
        return labels
