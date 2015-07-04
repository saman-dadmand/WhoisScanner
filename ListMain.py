__author__ = 'Saman'
if __name__ == '__main__':
    from config import config_section_map
    if config_section_map("general")['auto_start_search'] == 'True':
        import ListSearch
        ListSearch.main()
    else:

        ch=input('Choice Action:\n1:Create List\n2:Search Existed List:\n3:Export List Result\n0:Exit\n')
        if ch == '1':
            import ListCreator
            ListCreator.main()
        elif ch == '2':
            import ListSearch
            ListSearch.main()
        elif ch == '3':
            import ListExport
            ListExport.main()
