import numpy as np
import time
import nifty
import nifty.graph.rag as nrag
from elf.segmentation.watershed import distance_transform_watershed, apply_size_filter
from elf.segmentation.features import compute_rag
from elf.segmentation.multicut import multicut_kernighan_lin, transform_probabilities_to_costs
from plantseg import GenericProcessing


class MulticutFromPmaps(GenericProcessing):
    def __init__(self,
                 predictions_paths,
                 save_directory="MultiCut",
                 beta=0.5,
                 run_ws=True,
                 ws_2D=True,
                 ws_threshold=0.5,
                 ws_minsize=50,
                 ws_sigma=2.0,
                 ws_w_sigma=0,
                 post_minsize=50,
                 n_threads=6):

        super().__init__(predictions_paths,
                         input_type="data_float32",
                         output_type="labels",
                         save_directory=save_directory)

        # Multicut Parameters
        self.outputs_paths = []
        self.beta = beta

        # Watershed parameters
        self.run_ws = run_ws
        self.ws_2D = ws_2D
        self.ws_threshold = ws_threshold
        self.ws_minsize = ws_minsize
        self.ws_sigma = ws_sigma
        self.ws_w_sigma = ws_w_sigma

        # Post processing size threshold
        self.post_minsize = post_minsize

        # Multithread
        self.n_threads = n_threads

    def __call__(self):
        for predictions_path in self.predictions_paths:
            print(f"Segmenting {predictions_path}")
            output_path, exist = self.create_output_path(predictions_path,
                                                         prefix="_multicut",
                                                         out_ext=".h5")
            # Load file
            pmaps = self.load_stack(predictions_path)

            runtime = time.time()
            segmentation = self.segment_volume(pmaps)

            if self.post_minsize > self.ws_minsize:
                segmentation, _ = apply_size_filter(segmentation, pmaps, self.post_minsize)

            self.save_output(segmentation,
                             output_path,
                             dataset="segmentation")

            # stop real world clock timer
            runtime = time.time() - runtime
            self.runtime = runtime
            self.outputs_paths.append(output_path)
            print(" - Clustering took {} s".format(runtime))
        return self.outputs_paths

    def segment_volume(self, pmaps):
        if self.ws_2D:
            # WS in 2D
            ws = self.ws_dt_2D(pmaps)
        else:
            # WS in 3D
            ws, _ = distance_transform_watershed(pmaps, self.ws_threshold, self.ws_sigma, min_size=self.ws_minsize)

        rag = compute_rag(ws, 1)
        # Computing edge features
        features = nrag.accumulateEdgeMeanAndLength(rag, pmaps, numberOfThreads=1)  # DO NOT CHANGE numberOfThreads
        probs = features[:, 0]  # mean edge prob
        edge_sizes = features[:, 1]
        # Prob -> edge costs
        costs = transform_probabilities_to_costs(probs, edge_sizes=edge_sizes, beta=self.beta)
        # Creating graph
        graph = nifty.graph.undirectedGraph(rag.numberOfNodes)
        graph.insertEdges(rag.uvIds())
        # Solving Multicut
        node_labels = multicut_kernighan_lin(graph, costs)
        return nifty.tools.take(node_labels, ws)

    def ws_dt_2D(self, pmaps):
        # Axis 0 is z assumed!!!
        ws = np.zeros_like(pmaps)
        max_idx = 1
        for i in range(pmaps.shape[0]):
            _pmaps = pmaps[i]
            _ws, _ = distance_transform_watershed(_pmaps,
                                                  self.ws_threshold,
                                                  self.ws_sigma,
                                                  sigma_weights=self.ws_w_sigma,
                                                  min_size=self.ws_minsize)
            _ws = _ws + max_idx
            max_idx = _ws.max()
            ws[i] = _ws
        return ws
