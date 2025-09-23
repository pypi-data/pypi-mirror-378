#ifndef NETWORK_HPP
#define NETWORK_HPP
#include <random>
#include <unordered_set>
#include <utility>
#include <vector>
#define DEBUG_VAR(x) std::cout << #x << " = " << x << std::endl;
#include "Cartpole.hpp"
#include "Node.hpp"
#include "Fractal.hpp"
#include "GymnasiumWrapper.hpp"
#include <iostream>

/**
 * @class Network
 *
 * @brief This class defines the GNP graph.
 *
 * @param generator (std::shared_ptr<std::mt19937>): passes the generator for random values
 * @param jn (unsigned int): number of initial judgment nodes
 * @param jnf (unsigned int): number of judgment node functions 
 * @param pn (unsigned int): number of initial processing nodes
 * @param pnf (unsigned int): number of processing node funcions
 *
 */

class Network {
    private:
        std::shared_ptr<std::mt19937_64> generator;
    public:
        unsigned int jn;
        unsigned int jnf;
        unsigned int pn;
        unsigned int pnf;
        bool fractalJudgment; 
        std::vector<Node> innerNodes;
        Node startNode;
        float fitness = std::numeric_limits<float>::lowest();
        bool invalid = false; // to indicate invalid individuals
        int currentNodeID;
        int nConsecutiveP;
        std::unordered_set<int> usedNodes; // ids of nodes

        Network(
                std::shared_ptr<std::mt19937_64> _generator,
                unsigned int _jn,
                unsigned int _jnf,
                unsigned int _pn,
                unsigned int _pnf,
                bool _fractalJudgment
                ):
            generator(_generator),
            jn(_jn),
            jnf(_jnf),
            pn(_pn),
            pnf(_pnf),
            fractalJudgment(_fractalJudgment),
            startNode(generator,0,"S",-1) // init start node
            
    {
        startNode.setEdges("S", jn+pn);
        std::uniform_int_distribution<int> distributionJNF(0, jnf-1);
        for(int i=0; i<jn; i++){ // init judgment nodes 
            int randomInt = distributionJNF(*generator);
            innerNodes.push_back(Node(
                        generator, 
                        i, // node id 
                        "J", // node type 
                        randomInt // node function
                        ));
            if(fractalJudgment == false){
                innerNodes.back().setEdges("J", pn+jn);
            }else{
                std::pair<int, int> k_d = random_k_d_combination(pn+jn-1, generator);
                innerNodes.back().k_d.first = k_d.first;
                innerNodes.back().k_d.second = k_d.second;
                innerNodes.back().setEdges("J", pn+jn, pow(k_d.first,k_d.second));
            }
        }
        std::uniform_int_distribution<int> distributionPNF(0, pnf-1);
        for(int i=jn; i<jn+pn; i++){ // init procesing nodes 
            int randomInt = distributionPNF(*generator);
            innerNodes.push_back(Node(
                        generator, 
                        i, // node id 
                        "P", // node type 
                        randomInt // node function
                        ));
            innerNodes.back().setEdges("P", jn+pn);
        }
        
    }

        /**
         * @fn fitAccuracy
         * @brief executes transition path and calculates the accuracy.
         * @param X (std::vector<std::vector<int>>&) : X of data table (features) 
         * @param y (std::vector<int>&) : y of data table (target values) 
         * @param dMax (int) : maximal judgments until next decision
         * @param penalty (int) : devisor on fitness after exceeding maximal judgments
         */
        void fitAccuracy(
                const std::vector<std::vector<double>>& X,
                const std::vector<double>& y,
                int dMax,
                int penalty
                ){

            usedNodes.clear();
            int currentNodeID = startNode.edges[0];
            usedNodes.insert(currentNodeID);
            int dec;
            float correct = 0;
            for(int i=0; i<y.size(); i++){
                int  dSum = 0; // to prevent dead-looks 
                if (innerNodes[currentNodeID].type == "P"){
                    dec = innerNodes[currentNodeID].f;
                    if(dec == y[i]){
                        correct += 1;
                    }
                    currentNodeID = innerNodes[currentNodeID].edges[0];
                    usedNodes.insert(currentNodeID);
                } else if (innerNodes[currentNodeID].type == "J"){
                    while(innerNodes[currentNodeID].type == "J"){
                        float v = X[i][innerNodes[currentNodeID].f];
                        currentNodeID = innerNodes[currentNodeID].edges[innerNodes[currentNodeID].judge(v)];
                        usedNodes.insert(currentNodeID);
                        dSum += 1;
                        if (dSum >= dMax){
                            break;
                        }
                    }
                
                    dec = innerNodes[currentNodeID].f;
                    if(dec == y[i]){
                        correct += 1;
                    }
                }
                if (dSum >= dMax){
                    correct /= penalty;
                    break;
                }
            }
            fitness = correct / y.size();
        }

        template <typename dataContainer> // template for passing std::vector, std::array ...
        int decisionAndNextNode(const dataContainer& data, int dMax){
            int dec;
            int dSum = 0;
            double v;
            if(innerNodes[currentNodeID].type == "P"){
                dec = innerNodes[currentNodeID].f;
                // update currentNodeID to next node
                currentNodeID = innerNodes[currentNodeID].edges[0]; 
                usedNodes.insert(currentNodeID);
                nConsecutiveP ++;

            } else if (innerNodes[currentNodeID].type == "J"){
                nConsecutiveP = 0;
                while(innerNodes[currentNodeID].type == "J"){
                    // update currentNodeID to next node
                    v = data[innerNodes[currentNodeID].f];
                    currentNodeID = innerNodes[currentNodeID].edges[innerNodes[currentNodeID].judge(v)];
                    usedNodes.insert(currentNodeID);
                    dSum ++;
                    if (dSum >= dMax){
                        invalid = true;
                        return 0; // TODO is this a suitable value? 
                    }
                }
                dec = innerNodes[currentNodeID].f;
                // update currentNodeID to next node
                currentNodeID = innerNodes[currentNodeID].edges[0]; 
                usedNodes.insert(currentNodeID);
                nConsecutiveP ++;
           }
            return dec;
        }

        void fitGymnasium(
            GymEnvWrapper env,
            int dMax,
            int penalty,
            int maxSteps,
            int maxConsecutiveP,
            int worstFitness,
            int seed
            ){

            auto reset_out = env.reset();// Initial observation for the episode
            auto obs = reset_out[0].cast<std::vector<double>>();   
            auto info = reset_out[1];
            usedNodes.clear();
            currentNodeID = startNode.edges[0];
            usedNodes.insert(currentNodeID);
            int dec;
            fitness = 0;
            nConsecutiveP = 0;
            bool done = false;
            int steps = 0;

            while(done == false){
                dec = decisionAndNextNode(obs, dMax);
                auto result = env.step(dec);
                obs = result[0].cast<std::vector<double>>(); 
                fitness += result[1].cast<float>();
                steps ++;
                if(result[2].cast<bool>() || steps >= maxSteps) done = true; 

                if (invalid || nConsecutiveP > maxConsecutiveP){
                    done = true;
                    fitness = worstFitness;
                }
            }
        }
          
        void fitCartpole(
            int dMax,
            int penalty,
            int maxSteps,
            int maxConsecutiveP
            ){

            usedNodes.clear();
            currentNodeID = startNode.edges[0];
            usedNodes.insert(currentNodeID);
            int dec = 0;
            CartPole cp(generator);
            fitness = 0;
            nConsecutiveP = 0;
            std::array<double, 4> obs = cp.reset(); // Initial observation for the episode
            bool done = false;

            while(done == false){
                fitness ++;
                CartPole::StepResult result = cp.step(dec);
                obs = result.observation; 
                dec = decisionAndNextNode(obs, dMax);
                if(result.terminated || fitness >= maxSteps) done = true; 

                if (invalid || nConsecutiveP > maxConsecutiveP){
                    done = true;
                    fitness /= penalty;
                }
            }
        }

        void changeFalseEdges(){
            for(auto& node : innerNodes){
                std::uniform_int_distribution<int> distribution(0, innerNodes.size()-1);
                for(auto& edge : node.edges){
                    if(edge > innerNodes.size()-1){ // edge has no successor node -> set new one
                        node.changeEdge(innerNodes.size(), edge);
                    }
                }
            }
        }

        /*
         * @fn addDelNodes
         * @brief add and delete nodes to the individual (network)
         * @param minF (std::vector<float>&): min values of all features 
         * @param maxF (std::vector<float>&): min values of all features 
         */
        void addDelNodes(std::vector<float>& minF, std::vector<float>& maxF){ 
            std::bernoulli_distribution distributionBernoulliAdd(0.5);
            float pnRatio = static_cast<float>(pnf) / static_cast<float>(pnf+jnf);
            std::bernoulli_distribution distributionBernoulliProcessingNode(pnRatio);
            bool resultAdd = distributionBernoulliAdd(*generator);
            for(int n=0; n<innerNodes.size(); n++){
                if(resultAdd && usedNodes.size() >= innerNodes.size() * 1){// adding node hint 0.5 for more nodes in network
                    bool resultProcessingNode = distributionBernoulliProcessingNode(*generator);
                    if(resultProcessingNode){ // add processing node
                        std::uniform_int_distribution<int> distributionPNF(0, pnf-1);
                            int randomInt = distributionPNF(*generator);
                            innerNodes.push_back(Node(
                                        generator, 
                                        innerNodes.size(), // node id 
                                        "P", // node type 
                                        randomInt // node function
                                        ));
                            innerNodes.back().setEdges("P", innerNodes.size());
                            pn += 1;
                    }else{ // add judgment node 
                        std::uniform_int_distribution<int> distributionJNF(0, jnf-1);
                        int randomInt = distributionJNF(*generator);
                        innerNodes.push_back(Node(
                                    generator, 
                                    innerNodes.size(), // node id 
                                    "J", // node type 
                                    randomInt // node function
                                    ));
                       
                        if(fractalJudgment == true){
                            std::pair<int, int> k_d = random_k_d_combination(pn+jn, generator); // normaly pn+jn-1 but jn counter comes later
                            innerNodes.back().k_d.first = k_d.first;
                            innerNodes.back().k_d.second = k_d.second;
                            innerNodes.back().setEdges("J", pn+jn, pow(k_d.first,k_d.second));
                            innerNodes.back().productionRuleParameter = randomParameterCuts(innerNodes.back().k_d.first-1, generator);
                            std::vector<float> fractals = fractalLengths(innerNodes.back().k_d.second, sortAndDistance(innerNodes.back().productionRuleParameter));
                            innerNodes.back().setEdgesBoundaries(minF[randomInt], maxF[randomInt], fractals);
                        }else {
                            innerNodes.back().setEdges("J", innerNodes.size());
                            innerNodes.back().setEdgesBoundaries(minF[randomInt], maxF[randomInt]);
                        }

                        jn += 1;
                    }
                    break;

                }else if(!resultAdd && 
                        innerNodes.size()-usedNodes.size() > innerNodes.size() * 1 && // 1.5 
                        std::find(usedNodes.begin(), usedNodes.end(), innerNodes[n].id) == usedNodes.end()) // node is not used
                {// deleting nodes
                    for(int i=0; i<innerNodes.size(); i++){ // for each node
                        if(innerNodes[i].id > innerNodes[n].id){
                            innerNodes[i].id -= 1; // set back node numbers for nodes greater deleted id 
                        }
                        for(int k=0; k<innerNodes[i].edges.size(); k++){ // for each edge
                            if(innerNodes[i].edges[k] > innerNodes[n].id){
                                innerNodes[i].edges[k] -= 1; // change edges to reset node ids 
                            }else if(innerNodes[i].edges[k] == innerNodes[n].id){ // change edge pointing to deleted node
                                innerNodes[i].changeEdge(innerNodes.size()-1, innerNodes[i].edges[k]);
                            }
                        }
                    } 
                    startNode.changeEdge(innerNodes.size()-1, startNode.edges[0]);
                    if(innerNodes[n].type == "J"){
                        jn -= 1;
                    }else if (innerNodes[n].type == "P") {
                        pn -= 1;
                    }
                    innerNodes.erase(innerNodes.begin()+innerNodes[n].id);
                }
            }
        }

};

#endif
