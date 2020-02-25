

from process.globalutils import IP_GC


class IPService:
    '''
    service methods class for adding and removing ips for crawler

    '''

    def add(self, ip):
        '''
        adding ip to the list
        '''

        IP_GC.append(ip)

    def remove(self, ip):
        '''
        remove ip from the list
        '''
