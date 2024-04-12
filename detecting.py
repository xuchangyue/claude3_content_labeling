import base64
from claude3 import Claude3Wrapper
import os
import boto3

client = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")
wrapper = Claude3Wrapper(client)
# prompt = """
# 你是一个社交平台的图片审核AI助理，请帮助审查提供的图片是否含有暴力，色情等有害内容，如何有的话，直接回复Y-inappropriate，并给出理由。
# 如果图片无害，仔细检查图片，检查以下内容，如果有的话回复Yes，没有回复No：
#     - 是否有Rude Gesture，例如竖中指
#     - 是否有未成年人
#     - 是否有多个人
#     - 面部是否清晰可见
#     - 是否有戴口罩
#     - 是否有枪支
#     - 是否有名人，如果有的话，告诉我人名
# 并且回复一个列表，列出你观察到的物品或者对象。

# 以下是回复的例子：
# 如果图片有害：
# Y-inappropriate
# 如果图片无害：
#     - 是否有Rude Gesture，例如竖中指: No
#     - 是否有未成年人: No
#     - 是否有多个人: Yes
#     - 面部是否清晰可见: Yes
#     - 是否有戴口罩: No
#     - 是否有枪支: No
#     - 是否有名人: Taylor Swift
# [hat, glasses, beard]
# """
prompt = """
You are a content moderation expert, the following is our company's content moderation policy, based on the moderation policy, we gather text information from the user uploaded picture. moderation_policy:
    1. Explicit Nudity: it contains Nudity, Graphic Male Nudity, Graphic Female Nudity, Sexual Activity, Illustrated Explicit Nudity and Adult Toys.
    2. Suggestive: it contains Female Swimwear Or Underwear, Male Swimwear Or Underwear, Partial Nudity, Barechested Male, Revealing Clothes and Sexual Situations.
    3. Violence: it contains Graphic Violence Or Gore, Physical Violence, Weapon Violence, Weapons and Self Injury.
    4. Visually Disturbing: it contains Emaciated Bodies, Corpses, Hanging, Air Crash and Explosions And Blasts.
    5. Rude Gestures: it contains Middle Finger.
    6. Drugs: it contains Drug Products, Drug Use, Pills and Drug Paraphernalia.
    7. Tobacco: it contains contain Tobacco Products and Smoking.
    8. Alcohol: it contains Drinking and Alcoholic Beverages.
    9. Gambling: it contains Gambling.
    10. Hate Symbols: it contains Nazi Party, White Supremacy and Extremist.

    Based on the above Moderation policy, if the picture containes unsafe content, also give its category and reason. Please anwser the question with the following format : {
        "flag": "unsafe",
        "category": "xxx",
        "reason": "the reason is ..."
    }, and only put explanation into the reason field, Please answer the question with json format. 
    If the picture is safe, please tell the objects you observed in it, if there is any celeberity, tell the name. The answering format is:{
        "flag": "safe",
        "objects": ["xxxx", "celeberities":"Taylor Swift", "xxxxx"]
    }

"""
def image_to_base64(image_path):
    """
    将指定路径的图片转换成 Base64 编码的字符串。
    
    参数:
    image_path (str): 图片的文件路径。
    
    返回:
    str: 图片的 Base64 编码。
    """
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")
    return base64_image


def process_images_in_folder(folder_path, results_path):
    """
    遍历指定文件夹下的所有图片,将它们转换为 Base64 编码,并调用 Claude 3 多模态模型进行处理。
    将结果输出到一个文件中。
    
    参数:
    folder_path (str): 包含图片的文件夹路径。
    """
    
    result_file = open(results_path+'/'+folder_path.split('/')[-1]+".md", "w")
    for filename in os.listdir(folder_path):
        file_type = filename.split('.')[-1]
        if file_type in ["webp", "jpg", "png"]:
        # if filename.endswith(".webp") or filename.endswith(".jpg") or filename.endswith(".png"):
            image_path = os.path.join(folder_path, filename)
            base64_image = image_to_base64(image_path)
            sonnet_output = wrapper.invoke_claude_3_multimodal(prompt, base64_image, "sonnet")['content'][0]['text']
            haiku_output = wrapper.invoke_claude_3_multimodal(prompt, base64_image, "haiku")['content'][0]['text']
            result_file.write("# "+filename+"\n\n")
            result_file.write(f"![{filename}](data:image/{file_type};base64,{base64_image})\n\n")
            result_file.write("```\n")
            result_file.write(f"Sonnet:\n\n{sonnet_output}\n\n")
            result_file.write("```\n")
            result_file.write("```\n")
            result_file.write(f"Haiku:\n\n{haiku_output}\n\n")
            result_file.write("```\n")
    
    result_file.close()
    print("处理完毕,结果已保存到文件中。")

# 生成结果
folder_path = "./testing"
results_path = "./results"

for entry in os.listdir(folder_path):
    sub_folder = os.path.join(folder_path, entry)
    if os.path.isdir(sub_folder):
        process_images_in_folder(sub_folder, results_path)