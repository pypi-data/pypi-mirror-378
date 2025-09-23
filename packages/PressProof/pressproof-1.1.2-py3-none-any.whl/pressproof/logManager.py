import os

class LogManager:
    def __init__(self, args):
        self.args = args
        pass

    def logErrors(self, pageURL, title, errors):
        with open(f"{self.args.filename}.txt", "a") as file:
            logHeader = f"| {title} | {pageURL} |"
            logSpacer = "=" * len(logHeader)
            file.writelines(f"{logSpacer}\n{logHeader}\n")

            for error in errors: 
                snippet = error.get("snippet", "")
                issue = error.get("issue", "")

                file.writelines(f"Error: {snippet} | Issue: {issue}\n") 
        
                


