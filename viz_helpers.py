from analyzer import img2vec, image_from_url

def get_db(DATA_SOURCE=None):
    from os import environ
    from pymongo import MongoClient
    from dotenv import load_dotenv
    load_dotenv()
    
    database_url = {'api_database': environ['MONGO_URL'], 'scraping_database': environ['SCRAPING_URL'],  'list_files': None}
    database_url = database_url[DATA_SOURCE]
    
    cli = MongoClient(database_url)
    return cli

def load_images_tuple(DATA_SOURCE=None, cli=None, NUM_SAMPLES=None, FILE_URL=None):
    # TODO: keep images as a dict?
    # TODO: make a better model where I don't have to store all image_urls in memory
    if DATA_SOURCE == 'list_files':
        db_type = 'testing'
        images = []
        for i, x in enumerate(FILE_URL):
            images.append((i, x))

    # elif DATA_SOURCE == 'api_database':
        # TODO: api database needs to store URL to render similar images
        #db_type = 'mongo'
        #imageSearch = ImageSearch(db_type, None, threshold)
    #     pass

    elif DATA_SOURCE == 'scraping_database':
        db_type = 'testing'
        db = cli.publicData.priors
        images = []

        if NUM_SAMPLES == 'all':
            query = db.find({}, {'s3URL': 1})
        else: 
            query = db.aggregate([{"$sample": {"size": NUM_SAMPLES}}, {"$project": {"s3URL": 1}}])

        image_urls = [x['s3URL'].replace('/home/ubuntu/Downloads//', '') for x in list(query)]
        for i, x in enumerate(image_urls):
            images.append((i, x))
            
    return images, db_type, db

def build_search(images=None, db_type=None, THRESHOLD=None):
    from search import ImageSearch
    imageSearch = ImageSearch(db_type=db_type, db_filename=images)
    
    return imageSearch

def get_random_image(opt=None, image_url=None, images=None, db=None, DATA_SOURCE=None):
    # returns random image from data source
    from numpy.random import randint 

    if opt == 'from_sample':
        num_images = len(images)
        if num_images == 1:
            idx = 0
            image_url = images[0][1]
        else:
            idx = randint(len(images))
            image_url = images[idx][1]
        image = image_from_url(image_url)['image']
        return idx, image
    elif opt == 'from_url':
        image = image_from_url(image_url)['image']
        return 0, image
    elif DATA_SOURCE == 'single_file':
        num_images = len(images)
        i = randint(num_images)

        image_url = images[i][1]
        image = image_from_url(image_url)['image']

        return i, image
    elif DATA_SOURCE == 'api_database':
        # image_url = db.aggregate([{"$sample": 1}])
        pass
    elif DATA_SOURCE == 'scraping_database':
        query = db.aggregate([{"$sample": {"size": 1}}])
                
        image_url = list(query)[0]['s3URL'].replace('/home/ubuntu/Downloads//', '')
        image = image_from_url(image_url)['image']

        return 0, image
    else:
        return None
    
def get_default_transforms():
    transforms = {
        'None': (0, 0, 0), 
        'crop': (0, 0.5, 0.1),  # crop upto val*100 of each side
        'rotate': (0, 330, 30),   # rotate by angle
        'invert': (0, 0, 0), 
        'mirror': (0, 0, 0), 
        'BLUR': (0, 0, 0), 
        'CONTOUR': (0, 0, 0), 
        'DETAIL': (0, 0, 0), 
        'EDGE_ENHANCE': (0, 0, 0), 
        'EDGE_ENHANCE_MORE': (0, 0, 0), 
        'EMBOSS': (0, 0, 0), 
        'FIND_EDGES': (0, 0, 0), 
        'SMOOTH': (0, 0, 0), 
        'SMOOTH_MORE': (0, 0, 0), 
        'SHARPEN': (0, 0, 0), 
        'GaussianBlur(radius=param)': (0, 10, 0.5), 
        'UnsharpMask': (0, 0, 0), 
        'MedianFilter(size=int(param))': (1, 15, 2), 
        'MinFilter(size=int(param))': (1, 15, 2), 
        'MaxFilter(size=int(param))': (1, 15, 2), 
        'ModeFilter(size=int(param))': (1, 15, 2)
    }
    
    tf = 'None'    
    
    return transforms, tf

def get_transform(image, tf, param, imageSearch, doc_id=0, images=None):
    from transforms import imageTransforms

    imageTransformed = imageTransforms(image, type=tf, param=param)
    imageTransformedVec = img2vec(imageTransformed, type='image')

    ret = imageSearch.search(imageTransformedVec)            
    # only look at the top result, default is only one result
    new_doc_id = ret[0][0]
    new_doc_dist = ret[0][1]
    
    print(f'doc_id {doc_id} => {new_doc_id}')
    print(f'Transform {tf}: Distance={new_doc_dist}')

    if new_doc_id is not None:
        ret_image = image_from_url(images[new_doc_id][1])['image']
    else:
        ret_image = None
    
    return imageTransformed, ret_image, new_doc_id, new_doc_dist
    
def plot_transforms(image, imageTransformed, ret_image, new_doc_dist, tf):
    import matplotlib.pyplot as plt

    f, ax = plt.subplots(nrows=3, ncols=1, figsize=(10, 20))
    f.tight_layout()
    
    ax[0].imshow(image)
    ax[0].set_title('original image')
    ax[1].imshow(imageTransformed)
    ax[1].set_title(f'{tf} image')
    if ret_image is not None:
        ax[2].imshow(ret_image)
        ax[2].set_title(f'similar image: {new_doc_dist:.2f}')
        
def interact_setup(transforms, THRESHOLD, THRESHOLD_MIN, THRESHOLD_MAX, THRESHOLD_STEP):
    from ipywidgets import Dropdown, FloatSlider
    
    transformDropdown = Dropdown(
        options=list(transforms.keys()),
        description='Transform: ',
        value='None'
    )
    paramSlider = FloatSlider(
        value=0,
        min=transforms['None'][0],
        max=transforms['None'][1],
        step=transforms['None'][2],
        description='Param: '
    )
    thresholdSlider = FloatSlider(
        value=THRESHOLD,
        min=THRESHOLD_MIN,
        max=THRESHOLD_MAX,
        step=THRESHOLD_STEP,
        description='Threshold: '
    )

    def on_update_transform_widget(*args):
        # resetting range for incompatible ranges
        paramSlider.min=0
        paramSlider.max=100
        # actually setting range
        paramSlider.min = transforms[transformDropdown.value][0]
        paramSlider.max = transforms[transformDropdown.value][1]
        paramSlider.step = transforms[transformDropdown.value][2]

    transformDropdown.observe(on_update_transform_widget, 'value')
    
    return transformDropdown, paramSlider, thresholdSlider

def get_similar(image, num_similar, imageSearch, images):
    image_vec = img2vec(image, type='image')
    ret = imageSearch.search(image_vec, n=3)            

    ret_image = []
    for i, (doc_id, x) in enumerate(ret):
        if doc_id is not None:
            ret_image += [image_from_url(images[ret[i][0]][1])['image']]
        else:
            ret_image.append(None)
    
    return ret_image, ret
    
def plot_similar(image, ret_image, ret, num_similar, thresh=20):
    from math import ceil

    nrows = ceil(num_similar/2)
    ncols = 2
    f, ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=(10, 10))
    f.tight_layout()
    
    ax[0, 0].imshow(image)
    ax[0, 0].set_title('original image')
    
    num_similar_returned = len(ret_image)
    print(f'Found {num_similar_returned} similar posts out of {num_similar} requested with threshold {thresh}')
    for x in range(0, nrows):
        for y in range(0, ncols):
            if x == 0 and y == 0:
                continue
            i = x*2 + y
            try:
                ax[x, y].imshow(ret_image[i])
                ax[x, y].set_title(f'doc_id: {ret[i][0]} distance: {ret[i][1]:.2f}')
            except Exception as e:
                print(e)
                pass