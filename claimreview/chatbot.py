
import regex as re
class Chatbot:
    def __init__(self, chain):
        self.chain = chain

    def run(self, query):
        source_list = []
        answer = self.chain({"question": query}, return_only_outputs=True)
        for doc in answer.get("source_documents"):
            source_list.append(doc.metadata["source"])
        def extract_domain(url):
            match = re.search(r'^(?:https?:\/\/)?(?:[^@\/\n]+@)?(?:www\.)?([^:\/?\n]+)', url)
            return match.group(1) if match else None

        unique_domains = set()
        filtered_sourcelist = []

        for source in source_list:
            domain = extract_domain(source)
            if domain is not None and domain not in unique_domains:
                filtered_sourcelist.append(source)
                unique_domains.add(domain)

        sources = "\n".join(filtered_sourcelist)
        return "\n" + sources