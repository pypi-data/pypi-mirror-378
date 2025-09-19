import os
import shutil
from gensim.models import KeyedVectors
from gensim.scripts.glove2word2vec import glove2word2vec
from  gensim.models.fasttext import load_facebook_model
import json
import numpy as np
import zipfile
from pathlib import Path
import urllib.request


class EmbeddingLoader:
    class EmbeddingLoader:
        """
        Loads word or sentence embedding.

        Attributes
        ----------
        embeddings_raw : Any
            KeyedVectors format for static embeddings
        embeddings : np.ndarray
            Array of embeddings
        tokens : list of str
            Representative elements for the embeddings in natural language (words, sentences, or other elements to visualize)
        dimension : int
            Dimensionality of the embeddings.
        type: str
            Type of embedding
            - 'word': word embeddings
            - 'sentence': Sentence/document/passage embeddings
            - 'word_context': Word embeddings in different contexts  
            - 'custom': User-defined
        """
    def __init__(self):
        self.embeddings_raw = None 
        self.embeddings = None      
        self.tokens = None         
        self.dimension = None
        self.type = None
        self.embeddings_subset = None
        self.tokens_subset = None

        with open(os.path.join(os.path.dirname(__file__), 'pretrained_embeddings.json')) as f:
            self.available_pretrained = json.load(f)
            
    def get_cache_dir(self):
        cache_dir = Path.home() / ".wordviz_cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir   


    def _validate_file(self, path):
        '''checks if path argument leads to a valid file name and returns if it is binary'''
        valid_ext = ['.bin', '.txt', '.vec']

        if not isinstance(path, str):
            path = str(path)    
        _, ext = os.path.splitext(path.lower())

        if path is None:
            raise ValueError('File path is required')
        
        if not isinstance(path, str):
            raise TypeError('The file path must be a string')
        
        if not os.path.exists(path):
            raise FileNotFoundError(f"Invalid file path {path}: the file does not exist")
    
        if ext not in valid_ext:
            raise ValueError(f'Invalid file extension {ext}. Valid extensions are: {','.join(valid_ext)}')

        binary = True if ext == '.bin' else False

        return binary


    def load_from_file(self, path: str, format: str) -> np.ndarray:
        '''
        Loads word embeddings from a file in .txt, .vec, or .bin format.

        Parameters
        -----------
        path : str
            Path to the embedding file.
        format : str
            Format of the embedding model: 'word2vec', 'fasttext', or 'glove'.

        Returns
        --------
        np.ndarray
            Loaded embedding matrix.

        Notes:
        ------
        - For GloVe files, they are first converted to word2vec format.
        - FastText binary files are supported via Facebook's native loader.
        - Loaded tokens are stored in self.tokens.
        - Embedding matrix is stored in self.embeddings.
        '''

        binary = self._validate_file(path)

        match format:
            case 'word2vec':
                    self.embeddings_raw = KeyedVectors.load_word2vec_format(path, binary=binary)
            case 'fasttext':
                if binary:
                    self.embeddings_raw = load_facebook_model(path)
                else:
                    self.embeddings_raw = KeyedVectors.load_word2vec_format(path, binary=False)
            case 'glove':
                glove2word2vec(path, "glove_w2v.txt")
                if not os.path.exists("glove_w2v.txt"):
                    raise RuntimeError("GloVe to Word2Vec conversion failed.")
                
                self.embeddings_raw = KeyedVectors.load_word2vec_format("glove_w2v.txt")

        self.tokens = list(self.embeddings_raw.index_to_key)
        self.dimension = self.embeddings_raw.vector_size
        self.type = 'word'

        words = self.embeddings_raw.index_to_key
        self.embeddings = np.array([self.embeddings_raw.get_vector(word) for word in words])
        print("Embedding loaded from file")

        return self.embeddings
    

    def download_zip(self, url, filename):
        '''downloads zip file from url'''
        zip_path = self.get_cache_dir() / filename
        if not zip_path.exists():
            print(f"Downloading {filename}...")
            urllib.request.urlretrieve(url, zip_path)
        else:
            print(f"{filename} already exists in cache.")
        return zip_path
    

    def export_embedding(self, source_path, dest_folder):
        '''saves locally pretrained embeddings file'''
        os.makedirs(dest_folder, exist_ok=True)
        filename = os.path.basename(source_path)
        dest_path = os.path.join(dest_folder, filename)
        shutil.copy(source_path, dest_path)
        print(f"File saved in {dest_path}.")


    def load_pretrained(self, model: str, lang: str, source: str, dimension: str, save_file: bool = False, export_dir: str = None) -> np.ndarray:
        '''
        Downloads and loads a pretrained embedding model from an online source.

        Parameters
        -----------
        model : str
            Name of the embedding model ('word2vec', 'fasttext', etc.).
        lang : str
            Language code of the embedding ('en', 'it').
        source : str
            Data source ('wiki', 'cc').
        dimension : str or int
            Embedding dimensionality (e.g., '300').
        save_file : bool, default=False
            If True, saves the embedding to the specified export directory.
        export_dir : str, optional
            Path to the directory where the file will be exported (used if save_file=True).

        Returns
        --------
        np.ndarray
            Loaded embedding matrix (n_words x dimension).
        '''

        columns = self.available_pretrained["columns"]
        option = next(
            (dict(zip(columns, row)) for row in self.available_pretrained["data"]
            if row[0] == model and row[1] == lang and row[2] == source and row[3] == dimension),
            None
        )
        if option is not None:
            url = option['url']
            filename = option['filename']
        else:
            raise ValueError(f"Can't find pretrained file with parameters: {model}, {lang}, {source}, {dimension}")
        zip_filename = url.split("/")[-1]

        zip_path = self.download_zip(url, zip_filename)

        dest_dir = self.get_cache_dir() / model / lang / source / dimension
        dest_dir.mkdir(parents=True, exist_ok=True)
        file_path = dest_dir / filename

        if not file_path.exists():
            with zipfile.ZipFile(zip_path, 'r') as z:
                print(f"Extracting {filename}...")
                z.extract(filename, path=dest_dir)

        self.embeddings = self.load_from_file(file_path, model)

        if save_file:
                if export_dir is None:
                    raise ValueError("Must specify export_dir to save file.")
                self.export_embedding(file_path, export_dir)

        return self.embeddings
    
    
    def load_contextual(self, embeddings, labels, embedding_type='sentences') -> np.ndarray:
        """
        Loads embeddings from contextual models.
        
        Parameters
        -----------
        embeddings: various formats
            - numpy.ndarray
            - torch.Tensor
            - List[List[float]] 
        labels: list of str
            labels corresponding to embedding 
        embedding_type: str
            - 'sentence': Sentence/document/passage embeddings
            - 'word_context': Word embeddings in different contexts  
            - 'word': word embeddings
            - 'custom': User-defined
        Returns
        --------
        np.ndarray
            Loaded embedding matrix (n_labels x dimension).
        """
        
        embeddings_array = self._normalize_embeddings(embeddings)
        
        self.embeddings = embeddings_array  
        self.tokens = labels
        self.dimension = embeddings_array.shape[1]
        self.type = embedding_type
        print("Contextual embedding loaded")
        
        return self.embeddings

    def _normalize_embeddings(self, embeddings):
        """Converts embeddings to numpy array."""

        if isinstance(embeddings, np.ndarray):
            return embeddings.astype(np.float32)
         
        elif hasattr(embeddings, 'detach'):  # torch.Tensor
            return embeddings.detach().cpu().numpy().astype(np.float32)
        
        elif isinstance(embeddings, list):
            return np.array(embeddings, dtype=np.float32)
        
        else:
            try:
                return np.array(embeddings, dtype=np.float32)
            except:
                raise ValueError(f"Cannot convert embeddings of type {type(embeddings)} to numpy array")


    def list_available_pretrained(self):
        '''prints a list of pretrained embeddings provided by the package'''
        print('model | lang | source | dim')
        for file in self.available_pretrained['data']:
            print(" | ".join(x for x in file[:-2]))

    
    def get_embedding(self, token):
        '''returns corresponding embeddings using KeyedVectors object for a string given by the user'''
        if self.type in ["sentence", "word_context"]:
            index = self.tokens.index(token)
            return self.embeddings[index]
        elif self.type == "word":
            return self.embeddings[token]
        else:
            return None
            

    def subset(self, n: int = 1000, strategy: str = 'first', random_seed: int = None):
        '''
        Create a subset of the current embeddings and tokens. Useful for speeding up visualizations or 
        managing memory with large embedding spaces.

        Parameters
        -----------
        n : int, default=1000
            Number of embeddings to retain. If n exceeds the total number of available embeddings, all are retained.
        strategy : str, default='first'
            Selection strategy:
                - 'first': select the first n embeddings in original order.
                - 'random': select n random embeddings.
        random_seed : int, optional
            Seed for reproducible random sampling (only used if strategy is 'random').

        Updates
        --------
        self.tokens_subset : list of str
            List of selected token strings.
        self.embeddings_subset : np.ndarray
            Corresponding selected embedding vectors.
    '''
        if n > len(self.tokens):
            print('n is larger than the embedding size, the subset size will be equal to the full size')

        if strategy == 'first':
            indices = list(range(min(n, len(self.tokens))))
        elif strategy == 'random':
            rng = np.random.default_rng(random_seed)
            indices = rng.choice(len(self.tokens), size=min(n, len(self.tokens)), replace=False).tolist()
        else:
            raise ValueError("strategy has to be 'first' o 'random'")
        
        self.tokens_subset    = [self.tokens[i] for i in indices]
        self.embeddings_subset = self.embeddings[indices]


    def use_subset(self, n: int = 1000):
        '''returns embedding subset. If None, creates 1000 words subset and returns it.'''

        if self.embeddings_subset is None:
            self.subset(n)
        
        return self.embeddings_subset, self.tokens_subset