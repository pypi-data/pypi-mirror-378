//!  The Dowker complex of a hypergraph or binary relation

use std::cmp::Ordering;
use std::collections::HashMap;

use pyo3::exceptions::PyTypeError;
use pyo3::prelude::*;
use pyo3::types::IntoPyDict;
use pyo3::types::PyDict;
use pyo3::types::PyTuple;
use pyo3::wrap_pyfunction;
// use pyo3_log;

use itertools::Itertools;
use num::rational::Ratio;
use ordered_float::OrderedFloat;

use oat_rust::topology::simplicial::simplices::weighted::WeightedSimplex;
use oat_rust::algebra::chain_complexes::barcode::Bar;
use oat_rust::topology::simplicial::from::relation::DowkerComplex;
use oat_rust::topology::simplicial::from::relation::validate_dowker_boundary_matrix;
use oat_rust::topology::simplicial::simplices::vector::OrderOperatorTwistSimplex;

use oat_rust::algebra::matrices::operations::umatch::differential::DifferentialUmatch;
use oat_rust::algebra::vectors::operations::VectorOperations;
use oat_rust::algebra::matrices::query::{MatrixOracle, MatrixAlgebra};
use oat_rust::algebra::rings::types::native::FieldRationalSize;
use oat_rust::algebra::rings::types::native::RingOperatorForNativeRustNumberType;
use oat_rust::utilities::iterators::general::RequireStrictAscentWithPanic;
use oat_rust::utilities::order::JudgeOrder;
use oat_rust::utilities::order::{OrderOperatorByKey, OrderOperatorByKeyCustom};
use oat_rust::utilities::order::ReverseOrder;
use oat_rust::utilities::order::is_sorted_strictly;
use oat_rust::utilities::sequences_and_ordinals::SortedVec;


use crate::export::{IntoDataframeFormat};

type FilVal     =   OrderedFloat<f64>;
type RingElt    =   Ratio<isize>;


// pub struct DowkerComplexRational{
//     dowker_simplices_vec_format:    Vec<Vec<usize>>, 
//     maxdim:                         usize,
// }



// impl DowkerComplexRational{
//     fn indices_nzrow( &self ) -> Vec<Vec<usize>>;
//     fn indices_nzcol( &self ) -> Vec<Vec<usize>>;    
//     fn indices_homology( &self ) -> Vec<Vec<usize>>;        
//     fn betti_numbers() -> HashMap< isize: isize >;
//     fn jordan_column_for_hnumber( &self, colnum: usize ) -> Vec< ( Vec<usize>, isize, isize ) >;
//     fn matching_basis_vector_for_simplex( &self, colnum: usize ) -> Vec< ( Vec<usize>, isize, isize ) >;
// }


type Vertex = usize;
type RingOperator = RingOperatorForNativeRustNumberType< Ratio<isize> >;
type RingElement = Ratio<isize>;


/// Get the dimension of a simplex
/// 
/// This is intended for internal use within this module, only.
trait Dimension{
    fn dimension(&self) -> isize;
}

impl < T > Dimension for Vec< T > {
    fn dimension(&self) -> isize {
        self.len() as isize - 1
    }
}





#[pyclass(name="BoundaryMatrixDecompositionDowker")]
#[derive(Clone)]
/// A :term:`differential umatch decomposition` for the
/// boundary matrix of a Dowker complex, with rational coefficients.
/// This can be used to compute
/// 
/// - (co)homology groups
/// - (co)cycle representatives
/// - bounding chains
/// 
/// and more!
pub struct DowkerComplexDifferentialUmatch{
    differential_umatch:   DifferentialUmatch<
                    // matrix
                    DowkerComplex
                        < Vertex, RingOperator >,
                >,
    max_homology_dimension:     isize,
}


#[pymethods]
impl DowkerComplexDifferentialUmatch {


    /// Construct and factor the boundary matrix of a Dowker complex.
    /// 
    /// The resulting object can be used to compute homology, cycle spaces, boundaries, etc.
    /// 
    /// # Arguments
    /// 
    /// - `dowker_simplices`: A list of (sorted in strictly ascending order) lists of integers to use for initialization.        
    /// - `max_homology_dimension` the maximum dimension in which we want to compute homology
    #[new]
    pub fn new( 
            dowker_simplices:           Vec< Vec< Vertex > >,
            max_homology_dimension:     isize,
        ) -> 
        PyResult< Self >
    {
        let min_homology_dimension = 0;

        // convert the simplices to ordered vectors, for safety
        let dowker_simplices: Result< Vec<_>, _> = dowker_simplices.into_iter().map(|x| SortedVec::new(x) ).collect();

        match dowker_simplices {
            Ok( dowker_simplices ) => {
                // we use rational coefficients
                let ring_operator = FieldRationalSize::new();
                // construct the boundary matrix
                let boundary_matrix = DowkerComplex::new( dowker_simplices, ring_operator );
                // factor
                let differential_umatch = DifferentialUmatch::new(
                        boundary_matrix, 
                        min_homology_dimension,             
                        max_homology_dimension,
                    );   
                return Ok( DowkerComplexDifferentialUmatch{ differential_umatch, max_homology_dimension } )
            }, Err( unsorted_vec ) => {
                Err(PyErr::new::<PyTypeError, _>(
                    format!(
                        "One of the input vectors is not sorted in strictly ascending order: {:?}\n\
                        All input vectors (simplices) must be sorted in strictly ascending order. \
                        Please check your input and try again.",
                        unsorted_vec
                    )
                ))
            }
        }


    }    

    /// The maximum dimension for which we can recover information about
    /// homology, cycle spaces, boundaries, etc.
    pub fn max_homology_dimension( &self ) -> isize {
        self.max_homology_dimension.clone()
    }

    /// The sequence of row indices in the order visited when factoring the boundary matrix.
    /// 
    /// Returns the sequence of row indices of the boundary matrix sorted (first) 
    /// in ascending order of dimension, and (second) in descending lexicographic
    /// order (excluding simplices whose dimension strictly exceeds `self.max_homology_dimension()`)
    pub fn row_indices( 
        & self, 
    ) 
    -> Vec< Vec< Vertex > > { 
        self.differential_umatch.row_reduction_indices()
    }

    /// Returns the column indices of the differential COBM that collectively represent a basis for homology.
    pub fn homology_indices( 
            & self,
        ) -> Vec< Vec< Vertex > > 
    {
        self.differential_umatch.homology_indices()
    }

    /// Returns a column of the differential COBM
    pub fn matching_basis_vector_for_simplex<'py>(
            & self,
            simplex:        Vec< Vertex >,
            py:             Python< 'py >,
        ) -> PyResult< PyObject > {

        self.differential_umatch.differential_comb().column( &simplex ).collect_vec().into_dataframe_format(py)       
    }             

    /// Returns a column of the boundary matrix
    pub fn boundary<'py>(
            & self,
            index:          Vec< Vertex >,
            py:             Python< 'py >,
        ) -> PyResult<PyObject> {

        self.differential_umatch.boundary_matrix().column(&index).collect_vec().into_dataframe_format(py)
    }

    /// Returns a row of the boundary matrix
    pub fn coboundary<'py>(
            & self,
            index:          Vec< Vertex >,
            py:             Python< 'py >,
        ) -> PyResult<PyObject> {

            self.differential_umatch.boundary_matrix().row(&index).collect_vec().into_dataframe_format(py)
    } 

    /// Returns the index of the matched column of the boundary matrix (if it exists)
    pub fn get_matched_column(
        & self,
        index:         Vec< Vertex >
    ) -> Option< Vec<usize> > {    
        self.differential_umatch.generalized_matching_matrix().column_index_for_row_index(&index).clone()
    }            

    /// Returns the index of the matched row of the boundary matrix (if it exists)
    pub fn get_matched_row(
        & self,
        index:         Vec< Vertex >
    ) -> Option< Vec<usize> > {    
        self.differential_umatch.generalized_matching_matrix().row_index_for_column_index(&index).clone()
    }                

    /// The Betti numbers of the Dowker complex.
    /// 
    /// Returns a list [b_0, b_1, ..., b_max_homology_dimension], where b_i is the dimension of the i-th homology group.
    pub fn betti_numbers<'py>( & self ) -> Vec< isize > {
        let cycles      =   self.differential_umatch.cycle_space_dimensions();
        let bounds      =   self.differential_umatch.boundary_space_dimensions();
        let cycles = (0 .. self.max_homology_dimension + 1 ).map( |x| cycles.get(&x).cloned().unwrap_or(0) ).collect_vec();
        let bounds = (0 .. self.max_homology_dimension + 1 ).map( |x| bounds.get(&x).cloned().unwrap_or(0) ).collect_vec();
        let bettis = (0 .. self.max_homology_dimension as usize + 1 ).map( |x| cycles[x] - bounds[x] ).collect_vec();        

        return bettis
    }



    /// Dimensions of homology and the spaces of chains, cycles, boundaries
    /// 
    /// Each entry is the dimension of a vector space.
    pub fn fundamental_subspace_dimensions<'py>( & self, py: Python<'py> ) -> PyResult< Py<PyAny> > {
        let cycles      =   self.differential_umatch.cycle_space_dimensions();
        let bounds      =   self.differential_umatch.boundary_space_dimensions();
        let cycles = (0 .. self.max_homology_dimension + 1 ).map( |x| cycles.get(&x).cloned().unwrap_or(0) ).collect_vec();
        let bounds = (0 .. self.max_homology_dimension + 1 ).map( |x| bounds.get(&x).cloned().unwrap_or(0) ).collect_vec();
        let bettis = (0 .. self.max_homology_dimension as usize + 1 ).map( |x| cycles[x] - bounds[x] ).collect_vec();        
        let chains = cycles.iter().cloned().enumerate()
            .map(|(degree, c)| match degree == 0 { true=>{c},false=>{c+bounds[degree-1]} }).collect_vec();

        let dict = PyDict::new(py);
        dict.set_item( "homology",              bettis  )?;
        dict.set_item( "space_of_chains",       chains  )?;           
        dict.set_item( "space_of_cycles",       cycles  )?;
        dict.set_item( "space_of_boundaries",   bounds  )?;     
        
        let pandas = py.import("pandas")?;       
        let df: Py<PyAny> = pandas.call_method("DataFrame", ( dict, ), None)
            .map(Into::into)?;  
        let index = df.getattr( py, "index", )?;
        index.setattr( py, "name", "dimension", )?;
        return Ok(df)
    }    


    /// Runs a diagnostic to check that major and minor views of the dowker complex agree.
    pub fn diagnostic( &self, maxdim: isize ) {        
        let dowker_simplices = self.differential_umatch
            .boundary_matrix()
            .relation_rows()
            .clone();
        validate_dowker_boundary_matrix( dowker_simplices, maxdim );
    }

    /// Returns a data frame representing a basis for homology.
    /// 
    /// Each row of the data frame represents a homology class; together these homology
    /// classes form a basis for homology.  The data frame has the following columns:
    /// 
    /// - `dimension`: The dimension of the homology class
    /// - `cycle_representative`: A cycle representative for the homology class.
    ///   This is represented as a dataframe with columns `simplex` and `coefficient`.
    /// - `cycle_representative_nonzero_coefficient_count`: The number of nonzero coefficients in
    ///   the cycle representative.
    /// - `unique_simplex_id`: A simplex which can be used as a unique identifier for the homology class
    ///   (each homology class gets a different `unique_simplex_id`).
    /// 
    /// 
    ///   **Note: The `unique_simplex_id` corresponds to the birth simplex in persistent homology**.
    ///   The homology computation for Dowker complexes is implemented in essentially the same
    ///   way as a persistent homology computation -- with simplices ordered lexicographically.
    ///   The `unique_simplex_id` is simply the birth simplex from that computation.
    /// 
    pub fn homology<'py>( &self, py: Python<'py>) -> PyResult<PyObject> {
        let dict = PyDict::new(py);
        let harmonic_indices = self.homology_indices();

        let mut birth_simplices = Vec::new();
        let mut chains = Vec::new();
        let mut nnz = Vec::new();
        let mut dims = Vec::new();
        for birth_simplex in harmonic_indices {
            dims.push( birth_simplex.len()-1 );            
            let chain   =   self.differential_umatch
                .differential_comb()
                .column(&birth_simplex)
                .collect_vec();
            let simplex: pyo3::Bound<'_, PyTuple> = PyTuple::new(py, birth_simplex)?;
            birth_simplices.push( simplex );
            nnz.push( chain.len() );
            chains.push( chain.into_dataframe_format(py)? );
        }

        dict.set_item( "dimension", dims )?;
        dict.set_item( "cycle_representative", chains )?;
        dict.set_item( "cycle_representative_nonzero_coefficient_count", nnz )?; 
        dict.set_item( "unique_simplex_id", birth_simplices )?;        
        
        let pandas = py.import("pandas")?;       
        pandas.call_method("DataFrame", ( dict, ), None)
            .map(Into::into)
    }


    /// Optimize a cycle representative
    /// 
    /// Specifically, we employ the "edge loss" method to find a solution `x'` to the problem 
    /// 
    /// `minimize Cost(Ax + z)`
    /// 
    /// where 
    ///
    /// - `x` is unconstrained
    /// - `z` is a cycle representative for a (persistent) homology class associated to `birth_simplex`
    /// - `A` is a matrix composed of a subset of columns of the Jordna basis
    /// - `Cost(z)` is the sum of the absolute values of the products `z_s * filtration_value(s)`.
    /// 
    /// # Arguments
    /// 
    /// - The `birth_simplex` of a cycle represenative `z` for a bar `b` in persistent homology.
    /// - The `problem_type` type for the problem. The optimization procedure works by adding linear
    ///   combinations of column vectors from the Jordan basis matrix computed in the factorization.
    ///   This argument controls which columns are available for the combination.
    /// 
    ///   - (default) **"preserve PH basis"** adds cycles which appear strictly before `birth_simplex`
    ///     in the lexicographic ordering on filtered simplex (by filtration, then breaking ties by
    ///     lexicographic order on simplices) and die no later than `birth_simplex`.  **Note** this is
    ///     almost the same as the problem described in [Escolar and Hiraoka, Optimal Cycles for Persistent Homology Via Linear Programming](https://link.springer.com/chapter/10.1007/978-4-431-55420-2_5)
    ///     except that we can include essential cycles, if `birth_simplex` represents an essential class. 
    ///   - **"preserve PH basis (once)"** adds cycles which (i) are distince from the one we want to optimize, and
    ///     (ii) appear (respectively, disappear) no later than the cycle of `birth_simplex`.  This is a looser
    ///     requirement than "preserve PH basis", and may therefore produce a tighter cycle.  Note,
    ///     however, that if we perform this optimization on two or more persistent homology classes in a
    ///     basis of cycle representatives for persistent homology, then the result may not be a
    ///     persistent homology basis.
    ///   - **"preserve homology class"** adds every boundary vector
    ///   - "preserve homology calss (once)" adds every cycle except the one represented by `birth_simplex`
    /// 
    /// 
    /// 
    /// # Returns
    /// 
    /// A pandas dataframe containing
    /// 
    /// - `z`, labeled "initial_cycle"
    /// - `y`, labeled "optimal_cycle"
    /// - `x`, which we separate into two components: 
    /// 
    ///     - "surface_between_cycles", which is made up of codimension-1 simplices
    ///     - "difference_in_essential cycles", which is made up of codimension-0 simplices
    /// 
    /// - The number of nonzero entries in each of these chains
    /// - The objective values of the initial and optimized cycles
    /// 
    /// # Related
    /// 
    /// See
    /// 
    /// - [Escolar and Hiraoka, Optimal Cycles for Persistent Homology Via Linear Programming](https://link.springer.com/chapter/10.1007/978-4-431-55420-2_5)
    /// - [Obayashi, Tightest representative cycle of a generator in persistent homology](https://epubs.siam.org/doi/10.1137/17M1159439)
    /// - [Minimal Cycle Representatives in Persistent Homology Using Linear Programming: An Empirical Study With User’s Guide](https://www.frontiersin.org/articles/10.3389/frai.2021.681117/full)
    /// 
    #[pyo3(signature = (unique_simplex_id, problem_type, verbose=true))]
    pub fn optimize_cycle< 'py >( 
                &self,
                unique_simplex_id:      Vec< usize >,
                problem_type:           Option< &str >,
                verbose:                bool,
                py: Python< 'py >,
            ) -> PyResult<PyObject> // Option< &'py PyDict > { // MinimalCyclePyWeightedSimplexRational 
        {

        // inputs
        let matching_matrix                  =   self.differential_umatch.generalized_matching_matrix(); 
        let boundary_matrix                                    =   self.differential_umatch.boundary_matrix();       
        let order_operator                  =   self.differential_umatch.asymmetric_umatch().order_operator_for_row_entries_reverse();
        
        // matrix a, vector c, and the dimension function
        let dim_fn = |x: & Vec< usize > | x.len() as isize - 1 ;
        let obj_fn = |x: & Vec< usize > | 1.; 
        let a = |k: & Vec< usize >| self.differential_umatch.differential_comb().column_reverse( k ); 
             
        // column b
        let dimension = dim_fn( & unique_simplex_id );
        let b = self.differential_umatch.differential_comb().column_reverse( &unique_simplex_id );

        let column_indices = match problem_type.unwrap_or("preserve PH basis") {
            "preserve homology class"    =>  {
                self.differential_umatch
                    .boundary_space_indices() // indices of all boundary vectors in the jordan basis
                    .into_iter()
                    .filter(|x| x.dimension() ==dimension ) // of appropriate dimension    
                    .collect_vec()     
            }
            "preserve homology basis (once)"    =>  {
                self.differential_umatch
                    .cycle_space_indices() // indices of all boundary vectors in the jordan basis
                    .into_iter()
                    .filter(|x| (x.dimension()==dimension) && ( x != &unique_simplex_id) ) // of appropriate dimension 
                    .collect_vec()           
            }    
            _ => {
                return Err( PyErr::new::<pyo3::exceptions::PyValueError, _>( "Invaid input supplied for the `problem_type` keyword argument. This argument must be a string equal to either `preserve homology class` or `preserve homology basis (once)`.\nThis message is generated by OAT." ) );
            }                              
        };

        // solve
        let optimized = oat_rust::utilities::optimization::minimize_l1::minimize_l1(
            a, 
            b, 
            obj_fn, 
            column_indices,
            verbose
        ).unwrap();

        // formatting
        let to_ratio = |x: f64| -> Ratio<isize> { Ratio::<isize>::approximate_float(x).unwrap() };
        let format_chain = |x: Vec<_>| {
            let mut r = x
                .into_iter()
                .map(|(k,v): (Vec<_>,f64) | (k,to_ratio(v)))
                .collect_vec();
            // r.sort_by( |&(k,v), &(l,u)| order_operator.judge_cmp(&l, &k) );
            r.sort_by( |a,b| order_operator.judge_cmp(a, b) );
            r
        };
        
        // optimal solution data
        let x =     format_chain( optimized.x().clone() );        
        let cycle_optimal =     format_chain( optimized.y().clone() );
        let cycle_initial =     optimized.b().clone();        


        // triangles involved
        let bounding_difference             =   
            x.iter().cloned()
            .filter( |x| matching_matrix.has_a_match_for_row_index( &x.0) ) // only take entries for boundaries
            .map(|(k,v)| (matching_matrix.column_index_for_row_index( &k ).clone().unwrap(),v) )
            .multiply_self_as_a_column_vector_with_matrix_and_return_entries_in_reverse_order( self.differential_umatch.differential_comb() )
            .collect_vec();

        // essential cycles involved
        let essential_difference            =   
            x.iter().cloned()
            .filter( |x| matching_matrix.lacks_a_match_for_column_index( &x.0 ) ) // only take entries for boundaries
            .multiply_self_as_a_column_vector_with_matrix_and_return_entries_in_reverse_order( self.differential_umatch.differential_comb() )
            .collect_vec();       

        let objective_old               =   optimized.cost_b().clone();
        let objective_min               =   optimized.cost_y().clone();

        // let dict = PyDict::new(py);
        // dict.set_item( "birth simplex", birth_simplex.clone() )?;        
        // dict.set_item( "dimension", birth_simplex.len() as isize - 1 )?;
        // dict.set_item( "initial cycle objective value", objective_old )?;
        // dict.set_item( "optimal cycle objective value", objective_min )?;
        // dict.set_item( "initial cycle nnz", cycle_initial.len() )?;
        // dict.set_item( "optimal cycle nnz", cycle_optimal.len() )?;
        // dict.set_item( "initial_cycle", cycle_initial.export() )?;        
        // dict.set_item( "optimal_cycle", cycle_optimal.export() )?;
        // dict.set_item( "difference in bounding chains nnz", bounding_difference.len() )?;         
        // dict.set_item( "surface_between_cycles", bounding_difference.export() )?;   
        // dict.set_item( "difference in essential cycles nnz", essential_difference.len() )?;                                            
        // dict.set_item( "difference_in_essential cycles", essential_difference.export() )?;
        // dict.set_item( "before/after", beforeafter)?;



        //  CHECK THE RESULTS
        //  --------------------
        //
        //  * COMPUTE (Ax + z) - y
        //  * ENSURE ALL VECTORS ARE SORTED

        let ring_operator   =   boundary_matrix.ring_operator();
        let order_operator  =   ReverseOrder::new( OrderOperatorByKey::new() );        

        // We place all iterators in wrappers that check that the results are sorted
        let y   =   RequireStrictAscentWithPanic::new( 
                            cycle_optimal.iter().cloned(),  // sorted in reverse
                            order_operator,                 // judges order in reverse
                        );
        

        let z   =   RequireStrictAscentWithPanic::new( 
                            cycle_initial.iter().cloned(),  // sorted in reverse
                            order_operator,                 // judges order in reverse
                        );                                           
            
        // the portion of Ax that comes from essential cycles;  we have go through this more complicated construction, rather than simply multiplying by the jordan basis matrix, because we've changed basis for the bounding difference chain
        let ax0 =   RequireStrictAscentWithPanic::new( 
                            essential_difference.iter().cloned(),   // sorted in reverse
                            order_operator,                         // judges order in reverse
                        );                  

        // the portion of Ax that comes from non-essential cycles;  we have go through this more complicated construction, rather than simply multiplying by the jordan basis matrix, because we've changed basis for the bounding difference chain
        let ax1
            =   RequireStrictAscentWithPanic::new( 
                    bounding_difference
                        .iter()
                        .cloned()
                        .multiply_self_as_a_column_vector_with_matrix_and_return_entries_in_reverse_order(
                            self.differential_umatch.boundary_matrix()
                        ),  // sorted in reverse
                    order_operator,                 // judges order in reverse
                );  


        let ax_plus_z_minus_y
            =   RequireStrictAscentWithPanic::new( 
                    ax0.peekable()
                        .add(
                                ax1.peekable(),
                                ring_operator,
                                order_operator,
                            )
                        .peekable()
                        .add(
                                z.into_iter().peekable(),
                                ring_operator,
                                order_operator,
                            )
                        .peekable()
                        .subtract(
                                y.into_iter().peekable(),
                                ring_operator,
                                order_operator,
                            ),
                    order_operator,                 
                )
                .collect_vec();      

        // let 

        // let mut bounding_contribution_plus_z   
        //     = z.into_iter().peekable()
        //         .add(
        //             bounding_contribution.into_iter().peekable(), 
        //             self.factored.umatch().ring_operator(), 
        //             OrderOperatorByKey::new(),
        //         )
        //         .collect_vec();
        // bounding_contribution_plus_z.sort();
        // for p in 0..bounding_contribution_plus_z.len()-1{
        //     if bounding_contribution_plus_z[p].0 == bounding_contribution_plus_z[p+1].0{
        //         println!("\n\nError -- some cancellations did not occur.")
        //     }
        // }
        // let mut d = cycle_optimal.clone();
        // d.sort();
        // let e
        //     = bounding_contribution_plus_z.into_iter().peekable()
        //         .subtract(
        //             d.into_iter().peekable(), 
        //             self.factored.umatch().ring_operator(), 
        //             OrderOperatorByKey::new(),
        //         );

        // let tolerance   =   to_ratio( tolerance );
        // for (_,v) in e { assert!( v.abs() < tolerance ) }


        // !!! CHECK THQT VECTOR IS SORTED
        // println!(   "certificate this vector is the difference: {:?}", 
        //             a.peekable()
        //                 .add(
        //                     b.peekable(), 
        //                     self.factored.umatch().ring_operator(), 
        //                     ReverseOrder::new(OrderOperatorByKey::new()) 
        //                 )
        //                 .collect_vec() 
        //         );
        


        let dict = PyDict::new(py);

        // row labels
        dict.set_item(
            "type of chain", 
            vec![
                "initial_cycle", 
                "optimal_cycle", 
                "surface_between_cycles", 
                "difference in essential chains", 
                "Ax + z - y"
            ]
        )?;

        // objective costs
        dict.set_item(
            "cost", 
            vec![ 
                Some(objective_old), 
                Some(objective_min), 
                None, 
                None, 
                None, 
            ] 
        )?; 

        // number of nonzero entries per vector       
        dict.set_item(
            "nnz", 
            vec![ 
                cycle_initial.len(), 
                cycle_optimal.len(), 
                bounding_difference.len(), 
                essential_difference.len(),
                ax_plus_z_minus_y.len(),
            ] 
        )?;

        // vectors
        dict.set_item(
            "chain", 
            vec![ 
                cycle_initial.into_dataframe_format(py)?, 
                cycle_optimal.into_dataframe_format(py)?, 
                bounding_difference.into_dataframe_format(py)?, 
                essential_difference.into_dataframe_format(py)?,
                ax_plus_z_minus_y.into_dataframe_format(py)?
                ] 
        )?;   

        let pandas = py.import("pandas")?;       
        let dict = pandas.call_method("DataFrame", ( dict, ), None)
            .map(Into::< Py<PyAny> >::into)?;
        let kwarg = vec![("inplace", true)].into_py_dict(py)?;        
        dict.call_method( py, "set_index", ( "type of chain", ), Some(&kwarg));        

        return  Ok(dict)
    }     



}


//  =========================================
//  UTILITIES FOR LISTS OF LISTS
//  =========================================



// /// Compute basis of cycle representatives, over the rationals.
// /// 
// /// Input is a relation formatted vec-of-rowvec matrix.
// #[pyfunction]
// pub fn homology_basis_from_dowker( 
//             dowker_simplices_vec_format: Vec<Vec<usize>>, 
//             maxdim: isize
//         ) 
//     -> PyResult<Vec<Vec<Vec<(Vec<usize>,(isize,isize))>>>> {
//     // precompute the number of columns of the untransposed matrix
//     // note we have to add 1, since arrays are 0-indexed and we
//     // want to be able to use the max value as an index
//     let basis = 
//         oat_rust::topologysimplicial::from::relation::homology_basis_from_dowker(
//             & dowker_simplices_vec_format, 
//             maxdim,
//             FieldRationalSize::new(),
//             UseClearing::Yes,
//         );
//     let convert = |x: Ratio<isize> | (x.numer().clone(), x.denom().clone());
//     let basis_new = basis.iter().map(
//                 |x|
//                 x.iter().map(
//                     |y|
//                     y.iter().map(
//                         |z|
//                         (z.0.clone(), convert(z.1))
//                     ).collect()
//                 ).collect()
//             ).collect();

//     Ok(basis_new)
// }



//  =========================================
//  UTILITIES FOR LISTS OF LISTS
//  =========================================



/// Return the transpose of a list of lists
/// 
/// We regard the input as a sparse 0-1 matrix in vector-of-rowvectors format
#[pyfunction]
pub fn transpose_listlist( vecvec: Vec<Vec<usize>>) -> PyResult<Vec<Vec<usize>>> {
    // precompute the number of columns of the untransposed matrix
    // note we have to add 1, since arrays are 0-indexed and we
    // want to be able to use the max value as an index
    let ncol = vecvec.iter().flatten().max().unwrap_or(&0).clone() + 1; 
    let mut transposed = vec![vec![]; ncol];

    for (rowind, row) in vecvec.iter().enumerate() {
        for colind in row {
            transposed[*colind].push(rowind)
        }
    }
    Ok(transposed)
}

/// Return the transpose of a list of lists (SUBROUTINE)
/// 
/// We regard the input as a sparse 0-1 matrix in vector-of-rowvectors format
pub fn unique_row_indices_helper( vecvec:& Vec<Vec<usize>>) -> Vec<usize> {
    let mut uindices = Vec::new();
    let mut include;
    for (rowind, row) in vecvec.iter().enumerate() {
        include = true;
        for priorind in uindices.iter() {            
            if row == &vecvec[*priorind] { include = false; break }
        }
        if include { uindices.push(rowind) };
    }
    uindices
}

/// Returns indices for unique elements in a list of lists of integers
/// 
/// Concretely, if :math:`L = [L_1, \ldots, L_n]` is a list of lists of integers, then
/// this function returns a list of indices :math:`I = [i_1, \ldots, i_k]` such that
/// :math:`L_{i_1}, \ldots, L_{i_k}` are the unique elements of :math:`L`.
#[pyfunction]
pub fn unique_row_indices( vecvec: Vec<Vec<usize>>) -> PyResult<Vec<usize>> {
    Ok(unique_row_indices_helper( & vecvec))
}

/// Returns a list of unique elements in a list of lists of integers
/// 
/// Concretely, if :math:`L = [L_1, \ldots, L_n]` is a list of lists of integers, then
/// this function returns a list of lists :math:`U = [U_1, \ldots, U_k]` such that
/// :math:`U_{i_1}, \ldots, U_{i_k}` are the unique elements of :math:`L`.
#[pyfunction]
pub fn unique_rows( vecvec: Vec<Vec<usize>>) -> PyResult<Vec<Vec<usize>>> {
    let uindices = unique_row_indices_helper(&vecvec);
    let urows = uindices.iter().map(|x| vecvec[*x].clone() );
    Ok(urows.collect())
}