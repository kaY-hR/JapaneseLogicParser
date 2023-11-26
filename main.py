from knowledge_base import KnowledgeBase
from jp_grammer import JPGrammer
if __name__ == "__main__":
    kb = KnowledgeBase()

    kb.define("Father", "jiji", "chichi")
    kb.define("Father", "chichi", "me")
    kb.set_explanation("Father", "first-arg: father's name, second-arg: son's name")

    kb.define("Father", "me", "musuko")
    kb.define("Granpa", lambda X, *args: kb.check("Father", args[0], X) and kb.check("Father", X, args[1]))
    kb.define("GranGranpa", lambda X, Y, *args: kb.check("Father", args[0], X) and kb.check("Father", X, Y) and kb.check("Father", Y, args[1]))
    kb.define("Sunny")

    print(kb.check("Father", "chichi", "me"))
    print(kb.check("Father", "me", "chichi"))
    print(kb.check("Father", "jiji", "me"))
    print(kb.check("Father", "me", "musuko"))
    print(kb.check("Granpa", "jiji", "me"))
    print(kb.check("GranGranpa", "jiji", "musuko"))
    print(kb.find_solution(lambda unknown0, unknown1: kb.check("Granpa", unknown0, unknown1)))
    print(kb.find_solution(lambda unknown0, unknown1: kb.check("GranGranpa", unknown0, unknown1)))
    print(kb.check("Sunny"))

    print(kb.explain("Father"))

    # jg = JPGrammer(kb)

    # jg.set_grammer("Father", 
    #                {
    #                    "template":[
    #                        {"type":"variable", "name":"father"},
    #                        {"type":"syntax", "text":"は"},
    #                        {"type":"variable", "name":"son"},
    #                        {"type":"syntax", "text":"父である。"}
    #                    ]
    #                }
    #                )